from odoo import fields, models, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    rma_line_id = fields.Many2one('rma.lines', string='RMA Line')
    # rma_id = fields.Many2one('sale.rma', string='RMA')