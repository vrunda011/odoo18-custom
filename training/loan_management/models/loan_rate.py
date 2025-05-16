from odoo import models, fields, api

class LoanRate(models.Model):
    _name = 'loan.rate'
    _description = 'Loan Rate'

    rate = fields.Float(string='Rate of Interest')
    rate_date = fields.Date(string='Date')
    is_active = fields.Boolean(string='Is Active')
    loan_id = fields.Many2one('loan.loan', string='Loan Name')

    def action_is_active(self):
        active_rate_records = self.env['loan.rate'].search([
            ('is_active', '=', True), ('loan_id', '=', self.loan_id.id)])
        active_rate_records.write({'is_active': False})
        self.is_active = True
        self.loan_id.current_interest_rate = self.rate