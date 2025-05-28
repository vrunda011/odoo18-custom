from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(
        selection_add=[
            ('to approve', 'To Approve'), ('sale', '')
        ],
    )

    def _approval_allowed(self):
        """Returns whether the order qualifies to be approved by the current user"""
        self.ensure_one()
        amount = self.env['ir.config_parameter'].sudo().get_param('so_approval.sale_min_amount')

        if self.env['ir.config_parameter'].sudo().get_param('so_approval.is_sale_approval'):
            return (self.amount_total < float(amount)
                    or self.env.user.has_group('so_approval_system_param.group_sale_approver'))
        else:
            return True

    def button_approve(self, force=False):
        self.with_context(approved=True).action_confirm()

        # to_approve_orders = self.filtered(lambda order: order._approval_allowed())
        # if to_approve_orders:
        #     super(SaleOrder, self).action_confirm()

    def action_confirm(self):
        if self._context.get('approved'):
            super(SaleOrder, self).action_confirm()
        else:
            for order in self:
                if order.state not in ['draft', 'sent', 'to_approve']:
                    continue
                if order._approval_allowed():
                    order.button_approve()
                else:
                    order.write({'state': 'to approve'})

    def _confirmation_error_message(self):
        """ Return whether order can be confirmed or not if not then returm error message. """
        self.ensure_one()
        if self.state not in {'draft', 'sent', 'to approve'}:
            return "Some orders are not in a state requiring confirmation."
        if any(
            not line.display_type
            and not line.is_downpayment
            and not line.product_id
            for line in self.order_line
        ):
            return "A line on these orders missing a product, you cannot confirm it."

        return False