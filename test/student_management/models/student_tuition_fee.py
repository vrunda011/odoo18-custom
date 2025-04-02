from odoo import models, fields, api

STANDARD_VALUES = [('1','1'),
                   ('2','2'),
                   ('3','3'),
                   ('4','4'),
                   ('5','5'),
                   ('6','6'),
                   ('7','7'),
                   ('8','8'),
                   ('9','9'),
                   ('10','10'),
                   ('11','11'),
                   ('12','12')]

class TuitionFeeStructure(models.Model):
    _name = 'tuition.fee.structure'
    _description = 'Tuition Fee Structure'

    product_id = fields.Many2one('product.template',string='Product', domain=[('type', '=', 'service')])
    fee_amount = fields.Float(string='Fee Amount')
    quantity = fields.Float(string='Quantity')
    discount = fields.Float(string='Discount')
    subtotal = fields.Float(string='Sub Total', compute='_compute_sub_total', store=True)
    total = fields.Float(string='Total', compute='_compute_total', store=True)
    standard = fields.Selection(STANDARD_VALUES, string='Standard')

    @api.onchange('product_id')
    def _onchange_fee_amount(self):
        self.fee_amount = self.product_id.list_price

    @api.depends('fee_amount','quantity')
    def _compute_sub_total(self):
        for rec in self:
            rec.subtotal = rec.fee_amount * rec.quantity

    @api.depends('discount','subtotal')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.subtotal -((rec.subtotal*rec.discount)/100)