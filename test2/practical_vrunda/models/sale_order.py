from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[
            ('to approve', 'To Approve'), ('sale', '')
        ],
    )

    total_so_lines = fields.Integer(string="Total Service Products", compute='_compute_total_so_lines', store=True)

    @api.depends('order_line')
    def _compute_total_so_lines(self):
        for rec in self:
            rec.total_so_lines = len(rec.order_line.product_template_id.filtered(lambda r: r.type == 'service'))

    def action_view_add_product(self):
        view_id = self.env.ref('practical_vrunda.add_product_wizard_wizard').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quick Add',
            'res_model': 'add.product.wizard',
            'view_id': view_id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_confirm(self):
        if self._context.get('approved'):
            super(SaleOrder, self).action_confirm()

        else:
            for order in self:
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

    def button_approve(self, force=False):
        self.with_context(approved=True).action_confirm()

        to_approve_orders = self.filtered(lambda order: order._approval_allowed())
        if to_approve_orders:
            super(SaleOrder, self).action_confirm()

    def _approval_allowed(self):
        """Returns whether the order qualifies to be approved by the current user"""
        self.ensure_one()
        return (
                self.company_id.so_double_validation == 'one_step'
                or (self.company_id.so_double_validation == 'two_step'
                    and self.amount_total < self.env.company.currency_id._convert(
                    self.company_id.sale_min_amount, self.currency_id, self.company_id,
                    self.date_order or fields.Date.today()))
                or self.env.user.has_group('sales_team.group_sale_manager'))
