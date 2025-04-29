from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tags_ids = fields.Many2many('doc.tag.master', string="Doc Tags")
    document_ids = fields.Many2many('documents.custom', string="Documents")
    total_document = fields.Integer(string="Total Documents", compute='_compute_total_document', store=True)
    document_line_ids = fields.One2many('document.line', 'so_document_id', string="Line Ids")
    allow_value = fields.Boolean(string="Parameter Value", compute="_get_param_value")

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

            for rec in docs:
                doc_record = self.env['document.line'].search(
                    [('doc_id', '=', rec.id), ('so_document_id', '=', self.id)])
                if not doc_record:
                    self.env['document.line'].create({'doc_id': rec.id, 'so_document_id': self.id, 'product_ids': [(4, line.product_id.id)]})
                else:
                    doc_record.write({'product_ids': [(4, line.product_id.id)]})

        self.document_ids = [(6, 0, matching_docs.ids)]

        if self.user_id and self.user_id.login:
            self.action_send_mail_appointment()

    def action_confirm(self):
        res = super().action_confirm()
        self.picking_ids.document_ids = self.document_ids
        return res

    # send mail
    def action_send_mail_appointment(self):
        template_id = self.env.ref('bista_dms.email_template_get_documents')
        if template_id:
            template_id.send_mail(self.id, force_send=True)
        else:
            raise UserError("Mail Template not found. Please check the template.")

    @api.depends('document_ids')
    def _compute_total_document(self):
        for rec in self:
            rec.total_document = len(rec.document_ids)


    # Post message in Chatter
    def action_update_documents(self):
        self.message_post(body=f"Get document is performed {self.env.user}")

    # System Parameter
    def _get_param_value(self):
        for rec in self:
            value = self.env['ir.config_parameter'].sudo().get_param('can_update_document')
            if value=='1':
                rec.allow_value = True
            elif value=='0':
                rec.allow_value = False

    # Wizard
    def action_add_product_wizard(self):
        view_id = self.env.ref('bista_dms.add_product_wizard_wizard').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quick Add',
            'res_model': 'add.product.wizard',
            'view_id': view_id,
            'view_mode': 'form',
            'target': 'new',
        }
