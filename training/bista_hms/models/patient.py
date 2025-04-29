from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

BLOOD_GROUP = [('A+', 'A+ve'),
                ('B+', 'B+ve'),
                ('O+', 'O+ve'),
                ('AB+', 'AB+ve'),
                ('A-', 'A-ve'),
                ('B-', 'B-ve'),
                ('O-', 'O-ve'),
                ('AB-', 'AB-ve')]

class ResPatient(models.Model):
    _name = "res.patient"
    _description = "Patient"

    patient_code = fields.Char(string="Patient ID", default="New")
    partner_id = fields.Many2one('res.partner', string="Res Partner")
    name = fields.Char(string="Name", required=True)
    blood_group = fields.Selection(BLOOD_GROUP, string="Blood group", required=True)
    date_of_birth = fields.Date(string="Date of Birth", required=True)
    age = fields.Char(string="Age")
    age_category = fields.Selection([('child', 'Child'),
                                    ('minor', 'Minor'),
                                    ('adult', 'Adult'),
                                    ('senior', 'Senior Citizen')],
                                    string="Age Category")
    guardian_type = fields.Selection([('parent', 'Parent'),
                                      ('sibling', 'Sibling'),
                                      ('relative', 'Relative'),
                                      ('friend','Friend'),
                                      ('other','Other')],
                                     string="Guardian Type")
    guardian_id = fields.Many2one('res.partner','Guardian')
    previous_diseases = fields.Text(string="Previous Diseases")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")

    appointment_ids = fields.One2many("hms.appointment", "patient_id", string="Appointments")
    appointment_count = fields.Integer(string="Appointments", compute='_compute_appointment_count', default=0)
    weekly_visit = fields.Boolean(string="Weekly Visit", default=False)

    prescription_ids = fields.One2many("hms.prescription", "patient_id", string="Prescription Id")
    prescription_count = fields.Integer(string="Prescriptions", compute='_compute_prescription_count', default=0)

    partner_id = fields.Many2one("res.partner", string="Partner")

    # Name Search
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            domain = ['|', ('name', operator, name), ('phone', operator, name)]
            args.extend(domain)
            # records = self.sudo().search(args, limit=limit)
            # records.fetch(['display_name'])
            # return [(record.id, record.display_name) for record in records]
        else:
            return super().name_search(name, args, operator, limit)
        patient_ids = self.search_fetch(args, ['phone'], limit=limit)
        return [(patient_id.id, patient_id.display_name) for patient_id in patient_ids.sudo()]

    # Display Name
    @api.depends('patient_code', 'name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.patient_code}, {rec.name}"

    # Smart button method
    @api.depends('prescription_ids.patient_id')
    def _compute_prescription_count(self):
        for record in self:
            record.prescription_count = self.env['hms.prescription'].search_count([('patient_id', '=', record.id)])

    @api.depends('appointment_ids.patient_id')
    def _compute_appointment_count(self):
        for record in self:
            record.appointment_count = self.env['hms.appointment'].search_count([('patient_id', '=', record.id)])

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ResPatient, self).create(vals_list)
        for record in res:
            record.patient_code = self.env['ir.sequence'].next_by_code('res.patient')

        partner = self.env['res.partner'].create([{'name': res.name,
                                                   'phone': res.phone,
                                                   'email': res.email}])
        res.partner_id = partner.id

        return res

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if record.phone and len(record.phone) < 10:
                raise UserError("Phone number should be minimum 10 digits")

            patient_ids = self.env['res.patient'].search_count([('phone', '=', record.phone), ('id', '!=', record.id)])
            if patient_ids:
                raise UserError("Phone number already exists")

    # @api.constrains('date_of_birth')
    # def validation_constraints(self):
    #     today = fields.Date.today()
    #     for rec in self:
    #         if rec.date_of_birth >= today:
    #             raise ValidationError("Please enter correct date")

    @api.onchange('date_of_birth')
    def _onchange_date_of_birth(self):
        today = fields.Date.today()
        if self.date_of_birth and self.date_of_birth >= today:
            self.date_of_birth = False
            return {
                'warning': {
                    'title': "Invalid Date",
                    'message': "Birth date cannot be today or in the future.",
                }
            }

    @api.onchange('date_of_birth')
    def _onchange_age(self):
        today = date.today()
        diff = relativedelta(today, self.date_of_birth)
        if diff.years > 60:
            self.age_category = 'senior'
        elif diff.years > 18:
            self.age_category = 'adult'
        elif diff.years > 10:
            self.age_category = 'minor'
        else:
            self.age_category = 'child'

    def create_prescription(self):
        vals = {'patient_id': self.id,
                'date': fields.Datetime.now()}

        new_id = self.env['hms.prescription'].create(vals)
        new_id.state = 'confirmed'

    def action_appointments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointments',
            'view_mode': 'list,form',
            'res_model': 'hms.appointment',
            'domain': [('patient_id', '=', self.id)],
            'context': "{'default_patient_id': self.id}"
        }

    def action_open_appointments(self):
        view_id = self.env.ref('bista_hms.hms_appointment_form_view').id

        return {
            'name': 'Appointments',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hms.appointment',
            'view_id': view_id,
            'target': 'current',
            'context': {'default_patient_id': self.id}
        }

    def action_calculate_age(self):
        current_date = date.today()

        age_delta = relativedelta(current_date, self.date_of_birth)
        self.age = f"{age_delta.years} year(s) {age_delta.months} month(s)"

    def action_open_appointments(self):
        form_view_id = self.env.ref('bista_hms.hms_appointment_form_view').id
        list_view_id = self.env.ref('bista_hms.hms_appointment_list_view').id

        res = {
            'name': 'Appointments',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hms.appointment',
            'target': 'current',
            'view_id': form_view_id,
            'context': {'default_patient_id': self.id, 'child': True, 'name' : 'vrunda'}
        }

        if self.appointment_count >= 1:
            res['view_mode'] = 'list,form'
            res['views'] = [(list_view_id, 'list'), (form_view_id, 'form')]
            res['domain'] = [('patient_id', '=', self.id)]
            res['view_id'] = False

        return res

    def action_open_prescription(self):
        form_view_id = self.env.ref('bista_hms.prescription_form_view').id
        list_view_id = self.env.ref('bista_hms.prescription_list_view').id

        res = {
            'name': 'Prescriptions',
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'res_model': 'hms.prescription',
            'view_id': form_view_id,
            'target': 'current',
            'context': {'default_patient_id': self.id}
        }

        if self.prescription_count >= 1:
            res['view_mode'] = 'list,form'
            res['views'] = [(list_view_id, 'list'), (form_view_id, 'form')]
            res['domain'] = [('patient_id', '=', self.id)]
            res['view_id'] = False

        return res

    def _get_number_of_patient(self):
        print(self.env['res.patient'].search_count(
            [('date_of_birth', '<=', date.today().replace(year=date.today().year - 40))]))

    def _create_weekly_appointments(self):
            patients = self.search([('weekly_visit', '=', True)])

            for patient in patients:
                next_appointment_date = datetime.now() + timedelta(days=7)
                self.env['hms.appointment'].create({
                    'patient_id': patient.id,
                    'appointment_date': next_appointment_date,
                })
            # print("---weekly appointment----")

    # Write method
    def write(self, vals):
        if self.env.context.get('prevent_recursive_write_patient'):
            return super(ResPatient, self).write(vals)
        for patient in self:
            if patient.partner_id:
                partner_vals = {}
                if 'name' in vals:
                    partner_vals['name'] = vals['name']
                if 'phone' in vals:
                    partner_vals['phone'] = vals['phone']
                if 'mobile' in vals:
                    partner_vals['mobile'] = vals['mobile']
                if 'email' in vals:
                    partner_vals['email'] = vals['email']
                patient.partner_id.with_context(prevent_recursive_write_patient=True).write(partner_vals)

        if "phone" in vals:
            if len(vals.get("phone")) < 10 or len(vals.get("phone")) > 10:
                raise UserError("Enter 10 Digit Number")
        res = super(ResPatient, self).write(vals)
        return res
