from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        partner_id = vals.get('partner_id')
        template_id = vals.get('sale_order_template_id')

        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if partner.use_customers_tc and partner.tc:
                vals['note'] = partner.tc
            elif template_id:
                template = self.env['sale.order.template'].browse(template_id)
                if template.note:
                    vals['note'] = template.note

        return super(SaleOrder, self).create(vals)