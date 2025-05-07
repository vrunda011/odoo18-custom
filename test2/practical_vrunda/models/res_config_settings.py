from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_approval = fields.Boolean("Sale Order Approval", default=lambda self: self.env.company.so_double_validation == 'two_step')
    so_double_validation = fields.Selection(related='company_id.so_double_validation', string="Levels of Approvals *", readonly=False)
    sale_min_amount = fields.Monetary(related='company_id.sale_min_amount', string="Minimum Amount", currency_field='company_currency_id', readonly=False)

    def set_values(self):
        super().set_values()
        so_double_validation = 'two_step' if self.sale_approval else 'one_step'
        if self.so_double_validation != so_double_validation:
            self.so_double_validation = so_double_validation