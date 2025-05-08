from odoo import models, fields, api

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values):
        res = super()._get_stock_move_values(product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values)
        if values.get('location_id'):
            res.update({'location_id': values['location_id'].id })
        return res
