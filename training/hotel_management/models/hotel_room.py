from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HotelRoom(models.Model):
    _name = 'hotel.room'
    _description = 'Hotel Room'

    name = fields.Char(string="Room", default="New", help="Used to assign unique room number")
    category_id = fields.Many2one('hotel.room.category', string="Room Category")
    price_per_night = fields.Float(string="Price")
    status = fields.Selection([
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved')], string='Room Status')

    is_available = fields.Boolean(string="Is Available", compute='_compute_is_available', store=True)
    is_fixed = fields.Boolean(string="Mark as Fixed", default=False)
    reservation_ids = fields.Many2many('hotel.reservation', 'room_id', string="Reservations")
    housekeeping_ids = fields.One2many('housekeeping.task', 'room_id', string="Housekeeping Tasks")

    @api.model_create_multi
    def create(self, vals_list):
        res = super(HotelRoom, self).create(vals_list)
        for record in res:
            record.name = self.env['ir.sequence'].next_by_code('hotel.room')
        return res

    @api.depends('status')
    def _compute_is_available(self):
        """True if status is "Available" and not under maintenance."""
        for rec in self:
            if rec.status == 'available' or rec.status == 'maintenance':
                rec.is_available = True
            else:
                rec.is_available = False

    @api.onchange('category_id')
    def _onchange_category(self):
        """On change of room category, it sets the price for room."""
        self.price_per_night = self.category_id.price

    def action_mark_as_fixed(self):
        """
        This method is triggered by the 'Mark as Fixed' button.
        It checks if the current status is 'maintenance' and, if so, updates the status to 'available'.
        """
        for rec in self:
            if rec.status == 'maintenance':
                rec.write({
                    'status': 'available',
                    'is_fixed': True
                })

    def write(self, vals):
        """
        Override of the write method to
        ensures that rooms under maintenance cannot be marked as available or any other status
        until explicitly fixed.
        """
        for rec in self:
            prev_status = rec.status
            new_status = vals.get('status')
            if prev_status == 'maintenance' and new_status and new_status != 'maintenance':
                if not vals.get('is_fixed'):
                    raise ValidationError("You must mark the room as fixed before changing status from maintenance.")
        return super().write(vals)

