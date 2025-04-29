from odoo import fields, models, api

class RMAInvoiceLine(models.TransientModel):
    _name = 'rma.invoice.line'
    _description = 'RMA Invoice Lines'

    rma_invoice_id = fields.Many2one('rma.invoice.wizard', string="Wizard id")
    product_id = fields.Many2one('product.product', string="Product")
    so_qty = fields.Float(string="SO Qty")
    rma_lines_id = fields.Many2one('rma.lines', string="RMA line Id")
    to_invoiced = fields.Float(string="Qty to invoice")