from odoo import models, fields

class SubjectSubject(models.Model):
    _name = 'subject.subject'
    _description = 'Subject'

    name = fields.Char(string='Subject')