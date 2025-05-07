from odoo import fields, models, api

class AddProductWizard(models.TransientModel):
    _name = 'add.product.wizard'
    _description = 'Add Product Wizard'

    product_ids = fields.Many2many('product.product', string="Products")
    ticket_id = fields.Many2one('sale.order', string='Ticket Id')


    def action_add_product(self):
        self.ticket_id = self.env.context.get('active_id')
        product_list = []
        for line in self.product_ids:
            product_list.append((0, 0, {
                'name': line.name,
                'product_template_id': line.id,
            }))

        self.ticket_id.order_line = product_list

