from odoo import fields, models

class RMAWizardLine(models.TransientModel):
    _name = 'rma.wizard.line'
    _description = 'RMA Wizard Lines'

    rma_wizard_line_id = fields.Many2one('rma.wizard', string="RMA wizard line ID")
    product_id = fields.Many2one('product.product', string='Product')
    so_qty = fields.Float(string='SO Quantity')
    return_qty = fields.Float(string='Quantity')
    available_qty = fields.Float(string='Avail Quantity')
    rma_lines_id = fields.Many2one('rma.lines', string='RMA Lines')



