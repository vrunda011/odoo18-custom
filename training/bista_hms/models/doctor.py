from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResDoctor(models.Model):
    _name = "res.doctor"
    _description = "Doctor"

    name = fields.Char(string='Name')
    specialization = fields.Many2one("hospital.specialization", string="Specialization")
    license_no = fields.Char(string="License Number", required=True, unique=True)
    experience_years = fields.Integer(string="Experience (Years)")
    hospital_id = fields.Many2one("hospital.hospital", string="Associated Hospital/Clinic")
    is_emergency_available = fields.Boolean(string="Available for Emergency?")

    @api.constrains('license_no')
    def _check_unique_license_no(self):
        for record in self:
            if record.license_no:
                existing_records = self.search([
                    ('license_no', '=', record.license_no),
                    ('id', '!=', record.id)
                ])
                if existing_records:
                    raise ValidationError("License Number must be unique!")

