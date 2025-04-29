from odoo import models, fields, api

class StudentActivity(models.Model):
    _name = 'student.activity'
    _description = 'Student activity'

    name = fields.Char(string='Student Name')