from odoo import fields, models, api

class UpdateQtyWizard(models.TransientModel):
    _name = 'update.qty.wizard'
    _description = 'Update Quantity Wizard'

    location_id = fields.Many2one("stock.location", string="Location")
    qty = fields.Float(string="Quantity")

    def update_qty(self):
        if self.location_id:
            loc_id = self.location_id.id
            active_id = self.env.context.get('active_id')
            product_id = self.env['product.template'].browse(active_id)
            record = self.env['stock.quant'].search([('location_id', '=', loc_id), ('product_id', '=', product_id.product_variant_id.id)])
            record.write({'inventory_quantity': self.qty})
            record._apply_inventory()