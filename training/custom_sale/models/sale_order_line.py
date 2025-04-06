from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    extra_note = fields.Text(string='Extra Note')
    previous_price = fields.Float(string='Previous Price', compute="_compute_previous_price")
    # available_qty_wh = fields.Integer(string='WH Qty', compute='_compute_available_qty_wh', store=True)
    # location_ids = fields.Many2many('stock.location', widget="many2many_tags", string='Location')
    # available_qty_loc = fields.Integer(string='Loc Qty')

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

    # def _compute_available_qty_wh(self, product_id):
    #     for rec in self:
    #         rec.available_qty_wh = product_id.with_context(warehouse_id=rec.warehouse_id.id).qty_available
