from odoo import models, fields, api

class LoanTeamApprovalLevel(models.Model):
    _name = 'loan.team.approval.level'
    _description = 'Loan Team Approval Level'

    level_no = fields.Integer(string='Level', compute='_get_level_numbers')
    name = fields.Char(string='Name')
    user_ids = fields.Many2many('res.users', string='Users')
    team_id = fields.Many2one('loan.team', string='Team Name')

    @api.depends('team_id.level_ids')
    def _get_level_numbers(self):
        for rec in self:
            team_no = 0
            for level in rec.team_id.level_ids:
                team_no += 1
                level.level_no = team_no