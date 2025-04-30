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
        self.picking_ids.button_validate()
        self._create_invoices()
        self.invoice_ids.action_post()
        vals = self.invoice_ids.action_register_payment()

        wizard = self.env['account.payment.register'].with_context(vals['context']).create({})
        wizard._create_payments()


