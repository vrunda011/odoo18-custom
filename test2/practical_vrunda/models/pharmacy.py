from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Pharmacy(models.Model):
    _name = 'pr.pharmacy'
    _description = 'Pharmacy Model'

    name = fields.Char(String="Name")

    @api.constrains("name")
    def _check_duplicate_pharmacy_name(self):
        for record in self:
            existing_pharmacy_name = self.search([
                ("name", "=", record.name),
                ("id", "!=", record.id)
            ])
            if existing_pharmacy_name:
                raise ValidationError("Pharmacy name can not be duplicated!")