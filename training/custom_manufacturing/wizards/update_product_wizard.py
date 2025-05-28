from odoo import models, fields
import openpyxl
import base64
from io import BytesIO

class UpdateProductWizard(models.TransientModel):
    _name = 'update.product.wizard'
    _description = 'Update Product'

    operation_type = fields.Selection([('replace_product', 'Replace Product'),
                                    ('update_serial', 'Update Serial')], string='Operation Type')

    file = fields.Binary(string='Upload File')

    product_line_ids = fields.One2many('product.detail', 'product_id', string='Products')
    is_product_visible = fields.Boolean(string='Is Product Visible')

    def action_read_file(self):

        # read Excel file from Binary Field
        wb = openpyxl.load_workbook(
            filename=BytesIO(base64.b64decode(self.file)), read_only=True)
        ws = wb.active

        self.product_line_ids = [(5,0,0)]
        line_ids = []
        for record in ws.iter_rows(min_row=2, max_row=None, min_col=None, max_col=None, values_only=True):
            line_ids.append((0, 0, {
                'order_number': record[0],
                'current_product': record[1],
                'new_product': record[2],
            }))
        self.product_line_ids = line_ids
        self.is_product_visible = True

        view_id = self.env.ref('custom_manufacturing.update_product_wizard').id
        return {
            'name': 'Update Product/Serial',
            'view_mode': 'form',
            'res_model': 'update.product.wizard',
            'view_id': view_id,
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


