from odoo import api, fields, models

class MailActivitySchedule(models.TransientModel):
    _inherit = 'mail.activity.schedule'

    meaningful_conn = fields.Boolean(string="Meaningful Connection")