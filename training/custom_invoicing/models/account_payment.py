from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    remaining_amount = fields.Float(string='Remaining Amount', compute='_compute_remaining_amount', store=True)
    invoice_payment_line_ids = fields.One2many('invoice.payment.line', 'payment_id', string='Invoices')

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        invoice_ids = self.env['account.move'].search([('partner_id', '=', self.partner_id.id), ('move_type', '=', 'out_invoice'), ('amount_residual', '>', 0)])
        if invoice_ids:
            invoice_lines = []
            invoice_lines = [(5, 0, 0)]
            for line in invoice_ids:
                invoice_lines.append((0, 0, {
                    'invoice_id': line.id,
                    'date': line.invoice_date,
                    'amount': line.amount_residual,
                }))
            self.invoice_payment_line_ids = invoice_lines

    @api.onchange('amount')
    def _onchange_amount(self):
        if self.amount:
            remaining = self.amount
            for line in self.invoice_payment_line_ids:
                if remaining >= line.amount:
                    line.amount_allocation = line.amount
                    remaining -= line.amount
                else:
                    line.amount_allocation = remaining
                    remaining = 0

            self.remaining_amount = remaining

    @api.depends('invoice_payment_line_ids.amount_allocation')
    def _compute_remaining_amount(self):
        for rec in self:
            total_allocated_amount = sum(rec.invoice_payment_line_ids.mapped('amount_allocation'))
            for line in rec.invoice_payment_line_ids:
                allocated_amount = line.amount_allocation
                if allocated_amount > rec.amount:
                    raise UserError('Cannot allocate more than total payment.')
                if allocated_amount > line.amount:
                    raise UserError('Cannot allocate more than due amount.')
                if total_allocated_amount > rec.amount:
                    raise UserError('Total payment amount exceeds!')

            rec.remaining_amount = rec.amount - total_allocated_amount

    def action_post(self):
        res = super().action_post()
        for payment in self:
            move_lines = payment.move_id.line_ids
            for payment_line in payment.invoice_payment_line_ids:
                invoice_account_ids = payment_line.invoice_id.line_ids.mapped('account_id')
                matching_line = move_lines.filtered(lambda l: l.account_id in invoice_account_ids)
                if matching_line:
                    payment_line.invoice_id.js_assign_outstanding_line(matching_line.id)
        return res
