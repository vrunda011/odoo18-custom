from odoo import fields, models, api

class CRMPercentageStage(models.Model):
    _name = 'crm.percentage.stage'
    _description = 'Percentage Stages'

    name = fields.Char(string='Name')
    percentage = fields.Float(string='Percentage')

