from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    extra_discount = fields.Integer(string='Discount')