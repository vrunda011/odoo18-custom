from odoo import models, fields


class ProductDetail(models.TransientModel):
    _name = 'product.detail'
    _description = 'Product Details'

    order_number = fields.Char(string='MO number')
    current_product = fields.Char(string='Current Product')
    new_product = fields.Char(string='New Product')
    product_id = fields.Many2one('update.product.wizard', string='Product')
