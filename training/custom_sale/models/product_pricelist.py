from email.policy import default

from odoo import models, fields, api

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    is_special = fields.Boolean(string='Is Special Pricelist', default=False)

    @api.onchange('is_special')
    def onchange_is_special(self):
        if self.is_special == True:
            active_records = self.env['product.pricelist'].search([('is_special', '=', True)])
            for rec in active_records:
                rec.is_special = False

            self.is_special = True

