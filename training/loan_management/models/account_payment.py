from odoo import fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    loan_id = fields.Many2one('loan.loan', string='Loan Name')