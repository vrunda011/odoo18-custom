from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_approval = fields.Boolean(string="Sale Approval", config_parameter='so_approval.is_sale_approval')
    sale_min_amount = fields.Float(string="Minimum Amount", config_parameter='so_approval.sale_min_amount')