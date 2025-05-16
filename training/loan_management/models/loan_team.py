from odoo import models, fields, api

class LoanTeam(models.Model):
    _name = 'loan.team'
    _description = 'Loan Team'

    name = fields.Char(string='Team Name')
    level_ids = fields.One2many('loan.team.approval.level','team_id', string='Approval Levels')
