from odoo import models, fields

class HotelRoomCategory(models.Model):
    _name = 'hotel.room.category'
    _description = 'Hotel Room Category'

    name = fields.Char(string="Name")
    price = fields.Float(string="Price")