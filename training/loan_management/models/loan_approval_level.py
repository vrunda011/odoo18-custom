from email.policy import default

from odoo import models, fields, api

class LoanApprovalLevel(models.Model):
    _name = 'loan.approval.level'
    _description = 'Loan Approval Level'

    level_no = fields.Integer(string='Level', compute='_get_level_numbers')
    name = fields.Char(string='Name')
    user_ids = fields.Many2many('res.users', string='Users')
    stage = fields.Selection([
        ('pending','Pending'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string = 'Stage', default='pending')
    approved_by = fields.Char(string='Approved By')
    rejected_by = fields.Char(string='Rejected By')
    time = fields.Datetime(string='Time')
    loan_id = fields.Many2one('loan.loan', string='Loan Name')

    @api.depends('loan_id.approval_level_ids')
    def _get_level_numbers(self):
        for rec in self:
            loan_no = 0
            for level in rec.loan_id.approval_level_ids:
                loan_no += 1
                level.level_no = loan_no