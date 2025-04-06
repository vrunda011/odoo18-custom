from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self,vals):
        if self.env.context.get('prevent_recursive_write'):
            return super(ResPartner, self).write(vals)
        for rec in self:
            patient_record = self.env['res.patient'].search([('partner_id', '=', rec.id)])
            if patient_record.partner_id:
                patient_vals = {}
                if 'name' in vals:
                    patient_vals['name'] = vals['name']
                if 'phone' in vals:
                    patient_vals['phone'] = vals['phone']
                if 'mobile' in vals:
                    patient_vals['mobile'] = vals['mobile']
                if 'email' in vals:
                    patient_vals['email'] = vals['email']
                patient_record.with_context(prevent_recursive_write=True).write(patient_vals)

        res = super(ResPartner, self).write(vals)
        return res