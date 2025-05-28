# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _approval_allowed(self):
        """
        Override the method of purchase order
        Returns whether the order qualifies to be approved by the current user
        """
        self.ensure_one()
        return (
                self.company_id.po_double_validation == 'one_step'
                or (self.company_id.po_double_validation == 'two_step'
                    and self.amount_total < self.env.company.currency_id._convert(
                    self.company_id.po_double_validation_amount, self.currency_id, self.company_id,
                    self.date_order or fields.Date.today()))
                or self.env.user.has_group('purchase_approval.group_purchase_order_approver'))

    def button_confirm(self):
        res = super().button_confirm()
        for order in self:
            if order.state == 'to approve':
                template_id = self.env.ref('purchase_approval.email_template_purchase_approver')
                approver_ids = self.env['res.users'].search([("groups_id", "=", self.env.ref("purchase_approval.group_purchase_order_approver").id)])
                if template_id and approver_ids:
                    for user in approver_ids:
                        if user.email:
                            email_values = {
                                'email_to': user.email,
                            }
                            template_id.with_context({'user_name': user.name}).send_mail(order.id, force_send=True, email_values=email_values)
                else:
                    raise UserError("Mail Template not found. Please check the template.")
        return res

    # def get_approver_names(self):
    #     approver_ids = self.env['res.users'].search(
    #         [("groups_id", "=", self.env.ref("purchase_approval.group_purchase_order_approver").id)])
    #     return approver_ids