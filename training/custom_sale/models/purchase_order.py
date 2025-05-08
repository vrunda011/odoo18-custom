from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    category_id = fields.Many2one('product.category', string='Product Category')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(PurchaseOrder, self).create(vals_list)
        return res

    def _get_destination_location(self):
        res = super()._get_destination_location()
        for line in self.order_line:
            if line.location_final_id:
                return line.location_final_id.id
        return res
