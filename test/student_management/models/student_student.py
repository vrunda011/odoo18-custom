from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import UserError

STANDARD_VALUES = [('1','1'),
                   ('2','2'),
                   ('3','3'),
                   ('4','4'),
                   ('5','5'),
                   ('6','6'),
                   ('7','7'),
                   ('8','8'),
                   ('9','9'),
                   ('10','10'),
                   ('11','11'),
                   ('12','12')]

class ResStudent(models.Model):
    _name = 'res.student'
    _description = 'Student Details'

    registration_code = fields.Char(string='Registration ID', readonly=True, index=True, default="New")
    registration_date = fields.Date(string='Registration Date', required=True)
    name = fields.Char(string='Name', required=True)
    dob = fields.Date(string='Birth Date', required=True)
    age = fields.Char(string='Age')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    standard = fields.Selection(STANDARD_VALUES, string='Standard')
    gaurdian_name = fields.Char(string='Gaurdian Name')
    gaurdian_phone = fields.Text(string='Gaurdian Phone')
    tuition_fee = fields.Many2one('tuition.fee.structure', string='Tuition Fee Structure')
    is_blocked = fields.Boolean(string='Blocked', readonly=True)
    is_expired = fields.Boolean(string='Expired', readonly=True)
    previous_mark_ids = fields.One2many('previous.year.marks', 'student_id', string='Previous Year Marks')
    age_category = fields.Selection([('minor','Minor')])

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ResStudent, self).create(vals_list)
        for record in res:
            record.registration_code = self.env['ir.sequence'].next_by_code('res.student')
        return res

    @api.onchange('dob')
    def _onchange_age(self):
        if self.dob:
            current_date = date.today()

            age_delta = relativedelta(current_date, self.dob)
            self.age = f"{age_delta.years} years {age_delta.months} months"

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if record.phone and len(record.phone) < 10:
                raise UserError("Phone number should be minimum 10 digits")

            if record.phone and len(record.phone) > 10:
                raise UserError("Phone number must be 10 digits")

            if record.phone.isdigit():
                raise UserError("Phone number should contain digit only")

            student_ids = self.env['res.student'].search_count([('phone', '=', record.phone), ('id', '!=', record.id)])
            if student_ids:
                raise UserError("Phone number already exists")

    @api.onchange('dob')
    def _onchange_age_category(self):
        if self.dob:
            current_date = date.today()
            diff = relativedelta(current_date, self.dob)

            if diff.years < 10:
                self.age_category = 'minor'

    def action_block(self):
        self.is_blocked = True

    def action_unblock(self):
        self.is_blocked = False

    def _check_registration_expired(self):
        """It is a cron method that checks for the expired registrations"""
        expired_date = date.today() - timedelta(days=30)

        students = self.env['res.student'].search([
            ('is_blocked', '=', False),
            ('registration_date', '<=', expired_date),
        ])

        for student in students:
            student.is_expired = True

