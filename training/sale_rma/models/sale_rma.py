from odoo import models, fields, api

class SaleRMA(models.Model):
    _name = 'sale.rma'
    _description = 'RMA'

    rma_code = fields.Char(string='RMA ID', default='New')
    team_id = fields.Many2one('rma.team', string='Team', required=True)
    date = fields.Date(default=fields.Date.today)
    so_id = fields.Many2one('sale.order', string='Sale Order')

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
