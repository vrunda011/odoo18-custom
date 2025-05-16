from odoo import fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    loan_id = fields.Many2one('loan.loan', string='Loan Name')