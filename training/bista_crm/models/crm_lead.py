from odoo import models, fields, api

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    product_ids = fields.Many2many('product.product', string='Products')

    def _prepare_opportunity_quotation_context(self):
        res = super(CRMLead, self)._prepare_opportunity_quotation_context()
        product_lines = []
        for product in self.product_ids:
            product_lines.append((0, 0, {'product_id': product.id, }))
        res.update({'default_order_line': product_lines})
        return res