# -*- coding: utf-8 -*-

from odoo import fields, models

class SchoolManagement(models.Model):
    _name = "student.details"
    _description = "School Management"

    name = fields.Char("Name")
    address = fields.Text("Address")