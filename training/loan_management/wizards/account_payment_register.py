from datetime import date
from odoo import models
from odoo.exceptions import ValidationError

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        res = super().action_create_payments()
        today = date.today()
        invoice_id = self.env.context.get('active_id')
        invoice_rec = self.env['account.move'].search([('id', '=', invoice_id)])
        if invoice_rec.loan_id:
            if invoice_rec.amount_total == self.amount:
                emi_lines = invoice_rec.loan_id.emi_lines.filtered(lambda emi: emi.date == today)
                emi_lines.status = 'paid'
            else:
                raise ValidationError('Only full payments are valid for loan invoice')
        return res
