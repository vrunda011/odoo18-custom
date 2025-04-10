from odoo import fields, models, api

class RMAWizard(models.TransientModel):
    _name = 'rma.wizard'
    _description = 'RMA Wizard'

    rma_wizard_line_ids = fields.One2many('rma.wizard.line','rma_wizard_line_id', string="RMA Products")
    record_id = fields.Integer(string='Record Id')

    def default_get(self, fields_list):
        res = super(RMAWizard, self).default_get(fields_list)
        res['record_id'] = self.env.context.get('active_id')
        return res

    def process_return(self):
        pass

    @api.onchange('record_id')
    def onchange_sale_order(self):
        if self.record_id:
            records = self.env['sale.rma'].browse(self.record_id)
            rma_lines = []
            rma_lines = [(5, 0, 0)]
            for line in records.rma_line_ids:
                rma_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'so_qty': line.qty,
                }))
            self.rma_wizard_line_ids = rma_lines