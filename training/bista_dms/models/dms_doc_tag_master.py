from odoo import fields, models, api

class DocTagMaster(models.Model):
    _name = 'doc.tag.master'
    _description = 'Document Tag Master'

    name = fields.Char(string="Doc Tag Name")