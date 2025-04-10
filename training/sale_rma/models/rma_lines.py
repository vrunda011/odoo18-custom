from odoo import models, fields, api

class SaleRMA(models.Model):
    _name = 'rma.lines'
    _description = 'RMA lines'

    rma_line_id = fields.Many2one('sale.rma', string="RMA Line Id")
    product_id = fields.Many2one('product.product', string="Product")
    qty = fields.Float(string="Quantity")
    price = fields.Float(string="Unit Price")