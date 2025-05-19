from odoo import fields, models, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    serial_ids = fields.Many2many('stock.lot', string="Serial Numbers")

    def action_generate_serial_wizard(self):
        view_id = self.env.ref('custom_manufacturing.generate_sr_wizard').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generate Serial Number',
            'res_model': 'generate.serial.wizard',
            'view_id': view_id,
            'view_mode': 'form',
            'target': 'new',
        }

    def button_mark_done(self):
        res = super().button_mark_done()
        if self.state == 'done':
            self.serial_ids = [(3, self.lot_producing_id.id)]
        return res

    def action_update_product(self):
        view_id = self.env.ref('custom_manufacturing.update_product_wizard').id
        return {
            'name': 'Update Product/Serial',
            'view_mode': 'form',
            'res_model': 'update.product.wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }