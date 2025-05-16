from odoo import models, fields, api

class LoanEmi(models.Model):
    _name = 'loan.emi'
    _description = 'Loan EMI'

    date = fields.Date(string='Date')
    paid_amt = fields.Float(string='Principal Paid')
    int_charged = fields.Float(string='Interest Charged')
    total_payment = fields.Float(string='Total Payment')
    balance = fields.Float(string='Balance')
    loan_id = fields.Many2one('loan.loan', string='Loan Name')
    status = fields.Selection([('pending','Pending'),
                              ('generated','Invoice Generated'),
                              ('paid','Invoice Paid')
                              ], string='Status', default="pending")