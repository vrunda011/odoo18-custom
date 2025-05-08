from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Generate Serial Number
    def generate_serial_no(self):
        for move in self.move_ids:
            seq_id = move.product_id.sequence_id

            product_qty = int(move.quantity)
            for _ in range(product_qty):
                serial_no = seq_id.next_by_id()
                lot = self.env['stock.lot'].create({
                    'name': serial_no,
                    'product_id': move.product_id.id,
                })

                move.lot_ids = [(4, lot.id)]