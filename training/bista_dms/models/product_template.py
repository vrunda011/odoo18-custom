from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'product.template'

    doc_ids = fields.Many2many('documents.custom', string="Documents")
