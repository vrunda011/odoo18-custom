from odoo import models, fields, api

class SaleRMA(models.Model):
    _name = 'rma.lines'
    _description = 'RMA lines'

    rma_line_id = fields.Many2one('sale.rma', string="RMA Line Id")
    product_id = fields.Many2one('product.product', string="Product")
    qty = fields.Float(string="Quantity")
    price = fields.Float(string="Unit Price")
    move_ids = fields.One2many('stock.move', 'move_line_id', string='Move Id')
    to_receive_qty = fields.Float(string="To Receive", compute='_compute_to_receive_qty', store=True)
    received_qty = fields.Float(string="Received Qty", compute='_compute_to_received_qty', store=True)
    to_invoice_qty = fields.Float(string="To Invoice")
    invoiced_qty = fields.Float(string="Invoiced Qty")

    @api.depends('move_ids.state', 'move_ids.product_uom_qty')
    def _compute_to_receive_qty(self):
        for rec in self:
            rec.to_receive_qty = sum(rec.move_ids.filtered(lambda s: s.state not in ['done', 'cancel']).mapped('product_uom_qty'))

    @api.depends('move_ids.state', 'move_ids.quantity')
    def _compute_to_received_qty(self):
        for rec in self:
            rec.received_qty = sum(rec.move_ids.filtered(lambda m: m.state == 'done').mapped('quantity'))