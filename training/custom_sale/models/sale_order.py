from datetime import date

from odoo import models, fields, api
from num2words import num2words


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_to_words = fields.Text(string="In words", compute='compute_amount_to_words')
    discount_total_amount = fields.Float('Discount Amount', compute='_compute_discount_amount', store=True)

    @api.depends('order_line.price_unit', 'order_line.discount', 'order_line.product_uom_qty')
    def _compute_discount_amount(self):
        for order in self:
            total = 0.0
            for line in order.order_line:
                total += line.price_unit * ((line.discount or 0.0) / 100.0) * line.product_uom_qty
            order.discount_total_amount = total

    @api.model_create_multi
    def create(self, vals_list):
        # partner_id = vals.get('partner_id')
        for rec in vals_list:
            template_id = rec['sale_order_template_id']

            if rec['partner_id']:
                partner = self.env['res.partner'].browse(rec['partner_id'])
                if partner.use_customers_tc and partner.tc:
                    rec['note'] = partner.tc
                elif template_id:
                    template = self.env['sale.order.template'].browse(template_id)
                    if template.note:
                        rec['note'] = template.note

        return super(SaleOrder, self).create(vals_list)

    @api.depends('amount_total')
    def compute_amount_to_words(self):
        for rec in self:
            rec.amount_to_words = num2words(rec.amount_total, lang='en_IN', to='currency', currency='USD').title()

    def action_process_all(self):
        self.action_confirm()

        po = self._get_purchase_orders()
        if po:
            for order in po:
                order.button_confirm()

                # Assign Process Quantity for PO
                for po_line in order.order_line:
                    for move in po_line.move_ids:
                        for so_line in self.order_line:
                            if so_line.product_id.id == move.product_id.id:
                                move.quantity = so_line.process_qty

                # BACKORDER for PO
                order.action_view_picking()
                order.picking_ids.generate_serial_no()
                picking_vals = order.picking_ids.button_validate()
                if picking_vals != True:
                    pickings_to_validate = picking_vals['context']['button_validate_picking_ids']
                    pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate).with_context(skip_backorder=True)
                    pickings_to_validate.button_validate()

                # INVOICE for PO
                order.action_create_invoice()
                invoice_id = order.invoice_ids
                invoice_id.update({'invoice_date': date.today()})
                order.invoice_ids.action_post()
                # order.picking_ids.action_assign()

                # PAYMENT for PO bill
                payment_vals = order.invoice_ids.action_register_payment()
                self.env['account.payment.register'].with_context(payment_vals['context']).create({})._create_payments()


        # Assign Process Quantity for SO
        for order in self.order_line:
            for move in order.move_ids:
                move.quantity = order.process_qty

        # BACKORDER for SO
        picking_vals = self.picking_ids.button_validate()
        if picking_vals != True:
            pickings_to_validate = picking_vals['context']['button_validate_picking_ids']
            pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate).with_context(skip_backorder=True)
            pickings_to_validate.button_validate()

        # INVOICE for SO
        self._create_invoices()
        self.invoice_ids.action_post()
        vals = self.invoice_ids.action_register_payment()
        wizard = self.env['account.payment.register'].with_context(vals['context']).create({})
        wizard._create_payments()

    def action_create_delivery(self):
        for order in self:
            location_ids = []
            for line in order.order_line:
                if line.location_id and line.location_id.id not in location_ids:
                    location_ids.append(line.location_id.id)

            for loc in location_ids:
                vals = order.prepare_delivery_vals(loc)
                stock_picking_id = self.env['stock.picking'].create(vals)
                line_vals_list = order.prepare_delivery_line_vals(stock_picking_id, loc)
                self.env['stock.move'].create(line_vals_list)

    def prepare_delivery_vals(self, loc):
        delivery_type_id = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)
        values = {
            'partner_id': self.partner_id.id,
            'picking_type_id': delivery_type_id.id,
            'location_id': loc,
            'location_dest_id': delivery_type_id.default_location_dest_id.id,
            'sale_id': self.id,
            'origin': self.name
        }
        return values

    def prepare_delivery_line_vals(self, stock_picking_id, loc):
        line_vals_list = []
        for line in self.order_line:
            if line.location_id and line.location_id.id == loc:
                line_vals = {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'picking_id': stock_picking_id.id,
                    'location_id': stock_picking_id.location_id.id,
                    'location_dest_id': stock_picking_id.location_dest_id.id,
                    'name': line.name,
                    'sale_line_id': line.id
                }
                line_vals_list.append(line_vals)
        return line_vals_list

