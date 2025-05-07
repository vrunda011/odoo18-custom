from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pharmacy_id = fields.Many2one('pr.pharmacy', string="Pharmacy Id")
