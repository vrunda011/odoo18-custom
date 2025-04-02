from odoo import fields, models

class Hospital(models.Model):
    _name = "hospital.hospital"
    _description = "Hospital"

    name = fields.Char(string="Hospital Name", required=True)
    address = fields.Text(string="Address")
