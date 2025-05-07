from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleRMA(models.Model):
    _name = 'sale.rma'
    _description = 'RMA'
    _rec_name = 'rma_code'

    rma_code = fields.Char(string='RMA ID', default='New')
    team_id = fields.Many2one('rma.team', string='Team', required=True)
    date = fields.Date(default=fields.Date.today)
    so_id = fields.Many2one('sale.order', string='Sale Order')

    rma_line_ids = fields.One2many('rma.lines','rma_line_id', string="RMA Lines")
    picking_ids = fields.One2many('stock.picking', 'rma_id', string="Picking Ids")
    picking_count = fields.Integer(string="Picking", compute='_compute_picking_count', store=True)

    customer_id = fields.Many2one('res.partner', string='Customer')
    product_ids = fields.Many2many('product.product', string='Products', compute='_compute_rma_lines_product', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for rec in vals_list:
            if rec['team_id']:
                team = self.env['rma.team'].browse(rec['team_id'])
                prefix = team.prefix
                seq_name = f'Sale RMA {team.name}'
                seq_code = f'sale.rma.{team.id}'

                if not self.env['ir.sequence'].search([('code', '=', seq_code)], limit=1):
                    self.env['ir.sequence'].create({
                        'name': seq_name,
                        'code': seq_code,
                        'prefix': prefix,
                        'padding': 4,
                    })
                rec['rma_code'] = self.env['ir.sequence'].next_by_code(seq_code)
        return super(SaleRMA, self).create(vals_list)

    @api.onchange('so_id')
    def onchange_sale_order(self):
        rma_lines = []
        rma_lines = [(5, 0, 0)]
        for line in self.so_id.order_line:
            rma_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'qty': line.product_uom_qty,
                'price': line.price_unit,
            }))
        self.rma_line_ids = rma_lines

    def action_rma_wizard(self):
        view_id = self.env.ref('sale_rma.rma_wizard_wizard').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Return',
            'res_model': 'rma.wizard',
            'view_id': view_id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_open_picking(self):
        form_view_id = self.env.ref('stock.view_picking_form').id
        list_view_id = self.env.ref('stock.vpicktree').id

        res = {
            'name': 'picking',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'view_id': form_view_id,
            'target': 'current',
            'domain': [('rma_id', '=', self.id)],
        }

        if self.picking_count > 0:
            res['views'] = [(list_view_id, 'list'), (form_view_id, 'form')]
            res['domain'] = [('rma_id', '=', self.id)]
            res['view_mode'] = "form,list"
            res['view_id'] = False
        return res

    @api.depends('picking_ids')
    def _compute_picking_count(self):
        for record in self:
            record.picking_count = self.env['stock.picking'].search_count([('rma_id', '=', record.id)])

    def action_rma_invoice_wizard(self):
        view_id = self.env.ref('sale_rma.rma_invoice_wizard_view').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'rma.invoice.wizard',
            'view_id': view_id,
            'view_mode': 'form',
            'target': 'new',

        }

    # Add products into M2m field
    @api.depends('rma_line_ids.product_id')
    def _compute_rma_lines_product(self):
        for rec in self:
            products = []
            for line in rec.rma_line_ids:
                if line.product_id:
                    products.append(line.product_id.id)
            rec.product_ids = [(6, 0, products)]