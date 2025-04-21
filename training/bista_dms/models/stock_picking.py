from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    document_ids = fields.Many2many('documents.custom', string='Document Ids')

    @api.onchange('origin')
    def onchange_document_ids(self):
        self.document_ids = [(6, 0, self.origin.document_ids.ids)]
