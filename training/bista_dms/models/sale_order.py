from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tags_ids = fields.Many2many('doc.tag.master', string="Doc Tags")
    document_ids = fields.Many2many('documents.custom', string="Documents")

    @api.onchange('partner_id')
    def _onchange_get_tags(self):
        if self.partner_id:
            self.tags_ids = self.partner_id.tag_ids

    def action_get_documents(self):
        matching_docs = self.env['documents.custom']
        for line in self.order_line:
            product = line.product_template_id
            docs = product.doc_ids.filtered(lambda doc: any(tag in self.tags_ids for tag in doc.tag_ids))
            matching_docs |= docs

        self.document_ids = [(6, 0, matching_docs.ids)]

    def action_confirm(self):
        res = super().action_confirm()
        self.picking_ids.document_ids = self.document_ids
        return res
