from odoo import fields, models, api
from odoo.exceptions import ValidationError

class PrescriptionLine(models.Model):
    _name = "prescription.line"
    _description = "Prescription lines"

    prescription_id = fields.Many2one('hms.prescription', string='Prescription')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Integer(string='Quantity', default=1)
    price_unit = fields.Float(string='Unit Price', compute='_compute_price_unit', store=True)
    total = fields.Float(string='Total', compute='_compute_total', store=True)
    move_ids = fields.One2many('stock.move', 'prescription_line_id', string='Line Id')
    delivered_qty = fields.Integer(string="Delivered Quantity", compute="_compute_delivered_quantity", store=True)

    # def write(self, vals):
    #     if 'quantity' in vals:
    #         for line in self:
    #             if vals['quantity'] < line.quantity:
    #                 raise ValidationError("You cannot decrease the quantity once a delivery has been created.")
    #     return super(PrescriptionLine, self).write(vals)

    @api.constrains('quantity')
    def _check_quantity_increase(self):
        for line in self:
            delivered_qty = sum(line.move_ids.mapped('product_uom_qty'))
            if line.quantity < delivered_qty:
                raise ValidationError("You cannot decrease the quantity below the already delivered quantity.")

    @api.depends('product_id')
    def _compute_price_unit(self):
        for line in self:
            if line.product_id:
                line.price_unit = line.product_id.lst_price
            else:
                line.price_unit = 0.0

    @api.depends('quantity', 'price_unit')
    def _compute_total(self):
        for line in self:
            line.total = line.quantity * line.price_unit

    @api.depends('move_ids.state')
    def _compute_delivered_quantity(self):
        for line in self:
            line.delivered_qty = sum(line.move_ids.mapped(lambda record: record.quantity if record.state=='done' else 0))
