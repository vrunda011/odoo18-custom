from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Generate Serial Number
    def generate_serial_no(self):
        seq_id = self.move_ids.product_id.sequence_id
        product_qty = int(self.move_ids.quantity)
        for _ in range(product_qty):
            serial_no = seq_id.next_by_id()
            lot = self.env['stock.lot'].create({
                'name': serial_no,
                'product_id': self.product_id.id,
            })

            self.move_ids.lot_ids = [(4, lot.id)]