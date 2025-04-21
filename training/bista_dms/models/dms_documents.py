from odoo import fields, models, api

class DocumentsCustom(models.Model):
    _name = 'documents.custom'
    _description = 'Documents'

    name = fields.Char("Name")
    attachment_id = fields.Many2one('ir.attachment', string="Attachment Id")
    tag_ids = fields.Many2many('doc.tag.master', string="Tag Ids")