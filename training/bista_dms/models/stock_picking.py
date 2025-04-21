from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    document_ids = fields.Many2many('documents.custom', string='Document Ids')


