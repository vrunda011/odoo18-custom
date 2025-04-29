from odoo import fields, models, api

class DocumentLine(models.Model):
    _name = 'document.line'
    _description = 'Document Line'

    doc_id = fields.Many2one('documents.custom', string="Doc Id")
    product_ids = fields.Many2many('product.product', string="Product Id")
    so_document_id = fields.Many2one('sale.order', string="SO Id")
