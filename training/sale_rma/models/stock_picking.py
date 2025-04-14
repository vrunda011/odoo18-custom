from odoo import models,fields,api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    rma_id = fields.Many2one('sale.rma', 'RMA Id')
