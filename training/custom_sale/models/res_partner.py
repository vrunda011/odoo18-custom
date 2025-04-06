from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    extra_discount = fields.Integer(string='Discount')
    tc = fields.Text(string='Terms and Conditions')
    use_customers_tc = fields.Boolean(string='Use Customers T&C', default=False)