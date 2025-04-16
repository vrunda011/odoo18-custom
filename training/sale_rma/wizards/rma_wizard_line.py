from odoo import fields, models, api

class RMAWizardLine(models.TransientModel):
    _name = 'rma.wizard.line'
    _description = 'RMA Wizard Lines'

    rma_wizard_line_id = fields.Many2one('rma.wizard', string="RMA wizard line ID")
    product_id = fields.Many2one('product.product', string='Product')
    so_qty = fields.Float(string='SO Quantity')
    return_qty = fields.Float(string='Quantity')
    available_qty = fields.Float(string='Avail Quantity', compute='_compute_available_qty')
    rma_lines_id = fields.Many2one('rma.lines', string='RMA Lines')

    @api.depends('so_qty', 'rma_lines_id.to_receive_qty')
    def _compute_available_qty(self):
        for rec in self:
            used_qty = rec.rma_lines_id.to_receive_qty + rec.rma_lines_id.received_qty
            rec.available_qty = rec.so_qty - used_qty if rec.so_qty else 0.0