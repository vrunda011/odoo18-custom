from odoo import models, fields

class RMATeam(models.Model):
    _name = 'rma.team'
    _description = 'RMA Team'

    name = fields.Char(required=True)
    prefix = fields.Char(string='Sequence Prefix', required=True)
