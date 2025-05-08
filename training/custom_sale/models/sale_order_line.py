from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    extra_note = fields.Text(string='Extra Note')
    previous_price = fields.Float(string='Previous Price', compute="_compute_previous_price")
    available_qty_wh = fields.Float(string='WH Qty', compute='_compute_quantities')
    wh_location_ids = fields.Many2many('stock.location', string='WH Location')
    available_qty_loc = fields.Float(string='Loc Qty', compute='_compute_quantities')
    process_qty = fields.Float('Process Quantity')
    location_id = fields.Many2one('stock.location', string='Location')

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

    def _compute_quantities(self):
        for rec in self:
            rec.available_qty_loc = rec.product_id.with_context(location=rec.wh_location_ids.ids).qty_available
            rec.available_qty_wh = rec.product_id.with_context(warehouse_id=rec.order_id.warehouse_id.id).qty_available

    def _prepare_procurement_values(self, group_id):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        if self.location_id:
            res.update({
                'location_id': self.location_id
            })
        return res

