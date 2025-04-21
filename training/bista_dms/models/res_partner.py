from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    tag_ids = fields.Many2many('doc.tag.master', string="Doc Tags")