from odoo import models, fields, api

class InvoicePaymentLine(models.Model):
    _name = 'invoice.payment.line'
    _description = 'Invoice Payment Lines'

    invoice_id = fields.Many2one('account.move', string='Invoice')
    date = fields.Date(string='Invoice Date')
    amount = fields.Float(string='Due Amount')
    amount_allocation = fields.Float(string='Allocation')

    payment_id = fields.Many2one('account.payment', string='Payment')

    # @api.onchange('amount_allocation')
    # def onchange_amount_allocation(self):
    #     self.payment_id.remaining_amount = self.payment_id.amount - sum(self.payment_id.invoice_payment_line_ids.mapped('amount_allocation'))
    #     print(self.payment_id.remaining_amount)