from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Name Search
    @api.model
    def name_search(self, name='', args=None, operator='=', limit=100):
        if not args:
            args = []

        customer_id = self._context.get('customer_id')
        if customer_id:
            domain = [('partner_id', operator, customer_id)]
            args.extend(domain)
            self.env['sale.order'].sudo().search_read(domain, ['name', 'partner_id'])
        else:
            return super().name_search(name, args, operator, limit)

        orders = self.search_fetch(domain, ['display_name'], limit=limit)
        return [(order.id, order.display_name) for order in orders]

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #     print("search_read")
    #     customer_id = self._context.get('customer_id')
    #     if customer_id:
    #         domain = [('partner_id', '=', customer_id)]
    #     return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        customer_id = self._context.get('customer_id')
        if customer_id:
            domain += [('partner_id', '=', customer_id)]
        return super().web_search_read(domain, specification, offset=offset, limit=limit, order=order, count_limit=count_limit)