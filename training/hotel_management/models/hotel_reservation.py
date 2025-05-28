from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime

class HotelReservation(models.Model):
    _name = 'hotel.reservation'
    _description = 'Hotel Reservation Management'
    _rec_name = 'res_code'

    res_code = fields.Char(string="Reservation", default="New", help="Used to assign unique reservation number")
    guest_id = fields.Many2one('hotel.guest', string="Guest")
    room_ids = fields.Many2many('hotel.room', string="Rooms")
    check_in = fields.Datetime(string="Check-In")
    check_out = fields.Datetime(string="Check-Out")
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('checked_in','Checked In'),
            ('checked_out', 'Checked Out'),
        ], string="State", default="draft")
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id)
    amount_total = fields.Float(string="Total Amount", compute='_compute_amount_total', store=True)
    amount_paid = fields.Float(string="Paid Amount")
    payment_status = fields.Selection([
            ('paid', 'Paid'),
            ('not_paid', 'Not Paid'),
            ('partially', 'Partially Paid')
        ], string="Payment Status", default="not_paid", compute='_compute_payment_status', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(HotelReservation, self).create(vals_list)
        for record in res:
            record.res_code = self.env['ir.sequence'].next_by_code('hotel.reservation')
        return res

    @api.constrains('check_in', 'check_out')
    def _check_dates(self):
        """
        It ensures that check in and check out
        date must be today or future date.
        """
        for rec in self:
            now = datetime.now()
            if rec.check_in and rec.check_in < now:
                raise ValidationError("Check-In must be today or a future date.")
            if rec.check_out and rec.check_out < now:
                raise ValidationError("Check-Out must be today or a future date.")
            if rec.check_in and rec.check_out and rec.check_out < rec.check_in:
                raise ValidationError("Check-Out must be after Check-In.")

    @api.constrains('amount_paid')
    def _check_amount_paid(self):
        if self.amount_paid > self.amount_total:
            raise ValidationError("Your payment amount is exceeding the total amount.")

    @api.depends('check_in', 'check_out', 'room_ids')
    def _compute_amount_total(self):
        """This method calculates Total cost based on number of nights × price × no. of rooms"""
        for rec in self:
            total = 0.0
            if rec.check_in and rec.check_out and rec.room_ids:
                duration = (rec.check_out - rec.check_in).days
                for room in rec.room_ids:
                    total += room.price_per_night * duration
            rec.amount_total = total

    @api.depends('amount_total', 'amount_paid')
    def _compute_payment_status(self):
        """Update the status of Payment based on paid amount."""
        for rec in self:
            if rec.amount_total and rec.amount_paid:
                if rec.amount_paid < rec.amount_total:
                    rec.payment_status = 'partially'
                elif rec.amount_paid == rec.amount_total:
                    rec.payment_status = 'paid'
                else:
                    rec.payment_status = 'not_paid'

    def action_confirm_reservation(self):
        """
        This method triggers on button confirm,
        It confirms the reservation for customer.
        """
        template_id = self.env.ref('hotel_management.email_template_reservation_confirmed')
        for rec in self:
            if template_id and rec.guest_id.partner_id.email:
                template_id.send_mail(rec.id, force_send=True)
            else:
                raise UserError("Mail Template not found. Please check the template.")

            rec.state = 'confirmed'

            for room in rec.room_ids:
                room.write({
                    'reservation_ids' : [(4, rec.id)]
                })