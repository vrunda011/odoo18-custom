from odoo import models, fields

class RMATeam(models.Model):
    _name = 'rma.team'
    _description = 'RMA Team'

    name = fields.Char(string='Team Name')
    prefix = fields.Char(string='Sequence Prefix')
