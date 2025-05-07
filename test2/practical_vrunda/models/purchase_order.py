from odoo import fields, models, api
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        if self.partner_id and self.partner_id.email:
            self.action_send_mail_po()
        return res

    def action_send_mail_po(self):
        template_id = self.env.ref('practical_vrunda.email_template_purchase_order')
        if template_id:
            template_id.send_mail(self.id, force_send=True)
        else:
            raise UserError("Mail Template not found. Please check the template.")