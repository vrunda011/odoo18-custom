from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_update_quantity_wizard(self):
        view_id = self.env.ref('custom_sale.update_qty_wizard_wizard').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quick Update',
            'res_model': 'update.qty.wizard',
            'view_id': view_id,
            'view_mode': 'form',
            'target': 'new',
        }

