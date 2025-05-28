from datetime import date

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HousekeepingTask(models.Model):
    _name = 'housekeeping.task'
    _description = 'Housekeeping Task'
    _rec_name = 'room_id'

    room_id = fields.Many2one('hotel.room', string='Room', required=True)
    partner_id = fields.Many2one('res.partner', string='Assigned Partner', required=True)
    scheduled_date = fields.Date(string='Scheduled Date', required=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Cleaning Status', default='pending')
    is_done = fields.Boolean(string="Is Completed")

    @api.constrains('scheduled_date')
    def _check_scheduled_date(self):
        """ It ensures that scheduled_date should be today or future date. """
        for rec in self:
            today = date.today()
            if rec.scheduled_date and rec.scheduled_date < today:
                raise ValidationError("Scheduled date must be today or a future date.")

    def action_mark_as_complete(self):
        self.status = 'completed'
        self.is_done = True
