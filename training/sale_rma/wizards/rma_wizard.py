from odoo import fields, models, api
from odoo.exceptions import UserError


class RMAWizard(models.TransientModel):
    _name = 'rma.wizard'
    _description = 'RMA Wizard'

    rma_wizard_line_ids = fields.One2many('rma.wizard.line','rma_wizard_line_id', string="RMA Products")
    ticket_id = fields.Many2one('sale.rma', string='Ticket Id')

    @api.onchange('ticket_id')
    def onchange_sale_order(self):
        self.ticket_id = self.env.context.get('active_id')
        if self.ticket_id:
            rma_lines = []
            rma_lines = [(5, 0, 0)]
            for line in self.ticket_id.rma_line_ids:
                rma_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'so_qty': line.qty,
                    'rma_lines_id': line.id
                }))
            self.rma_wizard_line_ids = rma_lines

    # ------Create Picking------
    def action_create_picking(self):
        vals = self.prepare_picking_vals()
        stock_picking_id = self.env['stock.picking'].create(vals)
        line_vals_list = self.prepare_picking_line_vals(stock_picking_id)
        line_ids = self.env['stock.move'].create(line_vals_list)
        if not line_ids:
            stock_picking_id.unlink()
            raise UserError('Add Product!')
        # self.ticket_id.picking_ids.action_confirm()

    def prepare_picking_vals(self):
        picking_id = self.env['stock.picking.type'].search([('code', '=', 'incoming')], limit=1)
        self.ticket_id = self.env.context.get('active_id')
        values = {
            'partner_id': self.ticket_id.so_id.partner_id.id,
            'picking_type_id': picking_id.id,
            'location_id': picking_id.default_location_src_id.id,
            'location_dest_id': picking_id.default_location_dest_id.id,
            'origin': self.ticket_id.rma_code,
            'rma_id': self.ticket_id.id,
        }
        return values

    def prepare_picking_line_vals(self, stock_picking_id):
        line_vals_list = []
        for line in self.rma_wizard_line_ids:
            # delivered_qty = sum(line.move_ids.mapped('product_uom_qty'))
            # remaining_qty = line.quantity - delivered_qty

            # if remaining_qty > 0:
            line_vals = {
                'product_id': line.product_id.id,
                'product_uom_qty': line.return_qty,
                'picking_id': stock_picking_id.id,
                'location_id': stock_picking_id.location_id.id,
                'location_dest_id': stock_picking_id.location_dest_id.id,
                'name': line.product_id.display_name,
                'move_line_id': line.rma_lines_id.id,
            }
            line_vals_list.append(line_vals)
        return line_vals_list

    def _merge_moves(self, merge_into=False):
        return self

