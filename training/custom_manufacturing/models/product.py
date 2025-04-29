from odoo import fields, models, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    sequence_id = fields.Many2one('ir.sequence', string="Sequence")