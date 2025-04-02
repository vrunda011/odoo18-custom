from odoo import models,fields,api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    prescription_id = fields.Many2one('hms.prescription', 'Prescription Id')
