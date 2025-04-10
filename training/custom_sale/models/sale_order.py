from odoo import models, fields, api
from num2words import num2words


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_to_words = fields.Text(string="In words", compute='compute_amount_to_words')

    @api.model
    def create(self, vals):
        # partner_id = vals.get('partner_id')
        template_id = vals.get('sale_order_template_id')

        if vals['partner_id']:
            partner = self.env['res.partner'].browse(vals['partner_id'])
            if partner.use_customers_tc and partner.tc:
                vals['note'] = partner.tc
            elif template_id:
                template = self.env['sale.order.template'].browse(template_id)
                if template.note:
                    vals['note'] = template.note

        return super(SaleOrder, self).create(vals)

    @api.depends('amount_total')
    def compute_amount_to_words(self):
        for rec in self:
            rec.amount_to_words = num2words(rec.amount_total, lang='en_IN', to='currency', currency='USD').title()