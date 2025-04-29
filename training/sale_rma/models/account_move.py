from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    rma_id = fields.Many2one('sale.rma', string="Sale RMA")
    # rma_id = fields.Many2one('sale.rma', string='RMA')