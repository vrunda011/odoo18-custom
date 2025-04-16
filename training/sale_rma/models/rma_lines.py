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

    @api.depends('move_ids.state')
    def _compute_to_receive_qty(self):
        for rec in self:
            total_qty = sum(rec.move_ids.mapped('product_uom_qty'))
            rec.to_receive_qty = total_qty - rec.received_qty

    @api.depends('move_ids.quantity')
    def _compute_to_received_qty(self):
        for rec in self:
            rec.received_qty = sum(rec.move_ids.mapped('quantity'))