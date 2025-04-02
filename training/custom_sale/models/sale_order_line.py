from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    extra_note = fields.Text(string='Extra Note')
    previous_price = fields.Float(string='Previous Price', compute="_compute_previous_price")

    @api.depends('product_id', 'product_uom', 'product_uom_qty','order_id.partner_id')
    def _compute_discount(self):
        res = super(SaleOrderLine, self)._compute_discount()
        for order in self:
            order.discount = order.discount + order.order_partner_id.extra_discount
        return res

    @api.depends('product_template_id.list_price')
    def _compute_previous_price(self):
        for rec in self:
            rec.previous_price = rec.product_template_id.list_price
