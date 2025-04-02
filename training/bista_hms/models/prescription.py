from os import WCONTINUED

from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError


class HmsPrescription(models.Model):
    _name = "hms.prescription"
    _description = "Prescription"
    _rec_name = "patient_id"

    patient_id = fields.Many2one("res.patient", string="Patient")
    date = fields.Date(string="Date", default=fields.Date.today)
    state = fields.Selection([('draft','Draft'),
                              ('confirmed','Confirmed'),
                              ('canceled','Canceled')
                              ], string='State', default='draft')

    prescription_lines = fields.One2many("prescription.line", "prescription_id", string="Prescription Lines")
    total_amount = fields.Float(string="Total Amount", compute='_compute_total_amount')
    delivery_ids = fields.One2many('stock.picking', 'prescription_id', string="Delivery Ids")
    delivery_count = fields.Integer(string="Delivery", compute='_compute_delivery_count', default=0, store=True)

    def action_create_invoice(self):
        if not self.prescription_lines:
            raise ValidationError("Please add prescription lines before creating an invoice.")

        vals = self.prepare_invoice_vals()
        invoice_id = self.env['account.move'].create(vals)
        line_vals_list = self.prepare_invoice_line_vals(invoice_id)
        line_ids  = self.env['account.move.line'].create(line_vals_list)
        print(line_ids)

    def prepare_invoice_vals(self):
        values = {
            'move_type': 'out_invoice',
            'partner_id': self.patient_id.partner_id.id,
            'partner_shipping_id': self.patient_id.id,
            'invoice_origin': self.patient_id.name,
            'company_id': self.env.user.company_id.id,
            'invoice_line_ids': [],
            'user_id': self.env.user.id,
        }
        return values

    def prepare_invoice_line_vals(self, invoice_id):
        line_vals_list = []
        for line in self.prescription_lines:
            line_vals = {
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'discount': 0.0,
                'move_id': invoice_id.id,
            }
            line_vals_list.append(line_vals)
        return line_vals_list

    def action_create_delivery(self):
        vals = self.prepare_delivery_vals()
        stock_picking_id = self.env['stock.picking'].create(vals)
        line_vals_list = self.prepare_delivery_line_vals(stock_picking_id)
        line_ids = self.env['stock.move'].create(line_vals_list)
        if not line_ids:
            stock_picking_id.unlink()
            raise UserError('Add Product!')
        self.delivery_ids.action_confirm()

    def prepare_delivery_vals(self):
        delivery_id = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)
        values = {
            'partner_id': self.patient_id.partner_id.id,
            'picking_type_id': delivery_id.id,
            'location_id': delivery_id.default_location_src_id.id,
            'location_dest_id': delivery_id.default_location_dest_id.id,
            'origin': self.patient_id.name,
            'prescription_id': self.id,
        }
        return values

    def prepare_delivery_line_vals(self, stock_picking_id):
        line_vals_list = []
        for line in self.prescription_lines:
            delivered_qty = sum(line.delivery_line_ids.mapped('product_uom_qty'))
            remaining_qty = line.quantity - delivered_qty

            if remaining_qty>0:
                line_vals = {
                    'product_id': line.product_id.id,
                    'product_uom_qty': remaining_qty,
                    'picking_id': stock_picking_id.id,
                    'location_id': stock_picking_id.location_id.id,
                    'location_dest_id': stock_picking_id.location_dest_id.id,
                    'name': line.prescription_id,
                    'prescription_line_id': line.id
                }
                line_vals_list.append(line_vals)
        return line_vals_list

    @api.depends("prescription_lines.total")
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.prescription_lines.mapped('total'))

    def action_draft(self):
        self.state='draft'

    def action_confirmed(self):
        self.state = 'confirmed'

    def action_canceled(self):
        self.state = 'canceled'

    def action_open_delivery(self):
        form_view_id = self.env.ref('stock.view_picking_form').id
        list_view_id = self.env.ref('stock.vpicktree').id

        res = {
            'name': 'Delivery',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'view_id': form_view_id,
            'target': 'current',
            'domain': [('prescription_id', '=', self.id)],
        }

        if self.delivery_count > 0:
            res['views'] = [(list_view_id, 'list'), (form_view_id, 'form')]
            res['domain'] = [('prescription_id', '=', self.id)]
            res['view_mode'] = "form,list"
            res['view_id'] = False
        return res

    @api.depends('delivery_ids.prescription_id')
    def _compute_delivery_count(self):
        for record in self:
            record.delivery_count = self.env['stock.picking'].search_count([('prescription_id', '=', record.id)])