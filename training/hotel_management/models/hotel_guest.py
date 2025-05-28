from email.policy import default

from odoo import models, fields, api

class HotelGuest(models.Model):
    _name = 'hotel.guest'
    _description = 'Guest Management'
    _rec_name = 'name'

    name = fields.Char(string="Guest", default="New", help="Used to assign unique guest number")
    partner_id = fields.Many2one('res.partner', string="Name")
    nationality = fields.Char(string="Nationality")
    email = fields.Char(string="Email")
    mobile = fields.Char(string="Mobile")

    @api.depends('name', 'partner_id')
    def _compute_display_name(self):
        """Display name customization."""
        for rec in self:
            if rec.partner_id:
                rec.display_name = f"[{rec.name}], {rec.partner_id.name}"
            else:
                rec.display_name = rec.name

    @api.model_create_multi
    def create(self, vals_list):
        """Generate sequence code."""
        res = super(HotelGuest, self).create(vals_list)
        for record in res:
            record.name = self.env['ir.sequence'].next_by_code('hotel.guest')
        return res

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """On change of Partner, it sets email and mobile respectively."""
        self.email = self.partner_id.email
        self.mobile = self.partner_id.mobile