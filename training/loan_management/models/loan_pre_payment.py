from datetime import date

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LoanPayment(models.Model):
    _name = 'loan.payment'
    _description = 'Loan Pre Payment'

    payment_date = fields.Date(string='Date')
    amount = fields.Float(string='Payment Amount')
    payment_status = fields.Selection([
        ('paid', 'Paid'),
        ('not_paid', 'Not Paid'),
    ], default='not_paid', string='Payment Status')
    loan_id = fields.Many2one('loan.loan', string='Loan name')
    invoice_id = fields.Many2one('account.move', string="Advance Invoice")

    def action_pay_advance_payment(self):
        """generate invoice payment of advance payment"""
        vals = self.prepare_invoice_vals()
        invoice = self.env['account.move'].create(vals)
        line_vals = self.prepare_invoice_line_vals(invoice)
        line_ids = self.env['account.move.line'].create(line_vals)
        invoice.action_post()
        payment_vals = invoice.action_register_payment()
        self.env['account.payment.register'].with_context(payment_vals['context']).create({})._create_payments()
        self.invoice_id = invoice
        self.payment_status = 'paid'

    def prepare_invoice_vals(self):
        values = {
            'move_type': 'out_invoice',
            'partner_id': self.loan_id.partner_id.id,
            'partner_shipping_id': self.loan_id.id,
            'invoice_origin': self.loan_id.partner_id.name,
            'company_id': self.env.user.company_id.id,
            'invoice_line_ids': [],
            'user_id': self.env.user.id,
            'loan_id': self.loan_id.id
        }
        return values

    def prepare_invoice_line_vals(self, invoice):
        emi_product = self.env.ref('loan_management.loan_management_emi_product').id
        line_vals = {
            'product_id': emi_product,
            'quantity': 1,
            'price_unit': self.amount,
            'discount': 0.0,
            'tax_ids': [],
            'move_id': invoice.id,
        }
        return line_vals