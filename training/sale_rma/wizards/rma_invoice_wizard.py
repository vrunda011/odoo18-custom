from odoo import fields, models, api

class RMAInvoiceWizard(models.TransientModel):
    _name = 'rma.invoice.wizard'
    _description = 'RMA Invoice Wizard'

    ticket_id = fields.Many2one('sale.rma', string='Ticket Id')
    invoice_line_ids = fields.One2many('rma.invoice.line','rma_invoice_id', string='invoice lines')

    @api.onchange('ticket_id')
    def onchange_sale_rma(self):
        self.ticket_id = self.env.context.get('active_id')
        if self.ticket_id:
            invoice_lines = []
            invoice_lines = [(5,0,0)]
            for line in self.ticket_id.rma_line_ids:
                invoice_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'so_qty': line.qty,
                    'rma_lines_id': line.id,
                    'to_invoiced': line.to_invoice_qty
                }))
            self.invoice_line_ids = invoice_lines

    # --------Create Invoice---------------------
    def action_create_invoice(self):
        # if not self.prescription_lines:
        #     raise ValidationError("Please add prescription lines before creating an invoice.")

        vals = self.prepare_invoice_vals()
        invoice_id = self.env['account.move'].create(vals)
        print(invoice_id)
        line_vals_list = self.prepare_invoice_line_vals(invoice_id)
        line_ids = self.env['account.move.line'].create(line_vals_list)
        print("line_ids", line_ids)

    def prepare_invoice_vals(self):
        values = {
            'move_type': 'out_invoice',
            'partner_id': self.ticket_id.so_id.partner_id.id,
            'partner_shipping_id': self.ticket_id.so_id.partner_id.id,
            'invoice_origin': self.ticket_id.rma_code,
            'company_id': self.env.user.company_id.id,
            'user_id': self.env.user.id,
            'rma_id': self.ticket_id.id
        }
        return values

    def prepare_invoice_line_vals(self, invoice_id):
        line_vals_list = []
        for line in self.invoice_line_ids:
            line_vals = {
                'product_id': line.product_id.id,
                'quantity': line.to_invoiced,
                'price_unit': line.rma_lines_id.price,
                'move_id': invoice_id.id,
                'rma_line_id': line.rma_lines_id.id
            }
            line_vals_list.append(line_vals)
        return line_vals_list