from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(
        selection_add=[
            ('to approve', 'To Approve'), ('sale', '')
        ],
    )

    def action_confirm(self):
        for order in self:
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})

    def button_approve(self, force=False):
        self = self.filtered(lambda order: order._approval_allowed())
        self.write({'state': 'sale', 'date_order': fields.Datetime.now()})
        return {}

    def _approval_allowed(self):
        """Returns whether the order qualifies to be approved by the current user"""
        self.ensure_one()
        return (
            self.company_id.po_double_validation == 'one_step'
            or (self.company_id.po_double_validation == 'two_step'
                and self.amount_total < self.env.company.currency_id._convert(
                    self.company_id.po_double_validation_amount, self.currency_id, self.company_id,
                    self.date_order or fields.Date.today()))
            or self.env.user.has_group('sales_team.group_sale_manager'))
