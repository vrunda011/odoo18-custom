from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class HmsAppointment(models.Model):
    _name = "hms.appointment"
    _description = "Appointment"
    _rec_name = "patient_id"

    appointment_code = fields.Char(string="Appointment ID",copy=False, readonly=True, index=True, default="New")
    patient_id = fields.Many2one("res.patient", string="Patient")
    phone = fields.Char(string="Phone")
    appointment_date = fields.Datetime(string="Date", required=True, default=fields.Date.today())
    appointment_reason = fields.Text(string="Reason")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('waiting', 'Waiting'),
                              ('in_consultation', 'In Consultation'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')],
                             string="Status", default='draft')
    guardian_type = fields.Selection([('parent', 'Parent'),
                                      ('sibling', 'Sibling'),
                                      ('relative', 'Relative'),
                                      ('friend', 'Friend'),
                                      ('other', 'Other')],
                                     string="Guardian Type", readonly=True)
    guardian_id = fields.Many2one('res.partner', 'Guardian', readonly=True)

    consultation_start = fields.Datetime(string="Consultation Start", readonly=True)
    consultation_end = fields.Datetime(string="Consultation End", readonly=True)
    total_consultation_time = fields.Float(string="Total Consultation Time (Minutes)", readonly=True)

    service_product_id = fields.Many2one('product.product', string="Service", domain=[('type', '=', 'service')])


    @api.model_create_multi
    def create(self, vals_list):
        res = super(HmsAppointment, self).create(vals_list)
        for record in res:
            record.appointment_code = self.env['ir.sequence'].next_by_code('hms.appointment')
        return res

    @api.constrains('appointment_date')
    def _check_appointment_date(self):
        today = fields.Date.today()
        for rec in self:
            if  rec.appointment_date.date() < today:
                raise ValidationError("Please enter a correct date")

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id:
            self.phone = self.patient_id.phone
            self.guardian_type = self.patient_id.guardian_type
            self.guardian_id = self.patient_id.guardian_id

    @api.constrains("patient_id", "appointment_date")
    def _check_duplicate_appointment(self):
        for record in self:
            existing_appointment = self.search([
                ("patient_id", "=", record.patient_id.id),
                ("appointment_date", "=", record.appointment_date),
                ("id", "!=", record.id)
            ])
            if existing_appointment:
                raise ValidationError("A patient cannot have multiple appointments on the same day!")

    def unlink(self):
        # for rec in self:
        #     if rec.state not in ['draft', 'cancel']:
        #         raise ValidationError("You can not delete a record which is not in draft or cancel state")
        #
        check_ids = self.filtered(lambda s: s.state not in ['draft', 'cancel'])
        if check_ids:
            raise ValidationError("You can not delete a record which is not in draft or cancel state")
        return super(HmsAppointment, self).unlink()

    def action_confirm(self):
        self.state = 'confirm'

    def action_consultation(self):
        self.write({
            'state': 'in_consultation',
            'consultation_start': fields.Datetime.now()
        })

    def action_done(self):
        for record in self:
            if not record.consultation_start:
                record.consultation_start = fields.Datetime.now()

            record.consultation_end = fields.Datetime.now()

            if record.consultation_start and record.consultation_end:
                delta = record.consultation_end - record.consultation_start
                record.total_consultation_time = delta.total_seconds() / 60.0

            record.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    def _send_appointment_reminder_today(self):
        # Send appointment reminder to patients
        # This method will be called by a cron job
        start_day = datetime.today().replace(hour=0, minute=0, second=1, microsecond=0)
        end_day = datetime.today().replace(hour=23, minute=59, second=59, microsecond=0)
        appointment_ids = self.env['hms.appointment'].search([('appointment_date', '>=', start_day),
                                                              ('appointment_date', '<=', end_day), ])

        print(appointment_ids)

    def _generate_weekly_consultation_report(self):
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday() + 7)
        end_of_week = start_of_week + timedelta(days=6)

        appointments = self.env['hms.appointment'].search([
            ('appointment_date', '>=', start_of_week),
            ('appointment_date', '<=', end_of_week),
        ])

        total_appointments = len(appointments)
        total_consultation_time = timedelta()
        long_consultation_patients = []

        for appointment in appointments:
            if appointment.consultation_end and appointment.consultation_start:
                consultation_duration = appointment.consultation_end - appointment.consultation_start
                total_consultation_time += consultation_duration

                if consultation_duration > timedelta(hours=1):
                    long_consultation_patients.append(appointment.patient_id.name)

        report_data = {
            'total_appointments': total_appointments,
            'total_consultation_time': str(total_consultation_time),
            'long_consultation_patients': long_consultation_patients,
        }
        print("Weekly Consultation Report:", report_data)

    def _auto_cancel_overdue_appointments(self):
        overdue_appointments = self.env['hms.appointment'].search([
            ('state', '=', 'draft'),
            ('create_date', '<', datetime.now() - timedelta(hours=24)),
        ])

        for appointment in overdue_appointments:
            appointment.action_cancel()

        # print("-----------auto cancel-------------")

    def _weekly_cancellation_report(self):
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday() + 7)
        end_of_week = start_of_week + timedelta(days=6)

        cancelled_appointments = self.env['hms.appointment'].search([
            ('state', '=', 'cancelled'),
            ('appointment_date', '>=', start_of_week),
            ('appointment_date', '<=', end_of_week),
        ])

        report_data = []

        for appointment in cancelled_appointments:
            report_data.append({
                'appointment_number': appointment.appointment_code,
                'patient': appointment.patient_id.name,
                'appointment_date': appointment.appointment_date.strftime('%Y-%m-%d'),
            })


        print("Weekly Cancellation Report:", report_data)
        # print("-----------cancelled report-------------")

    # @api.depends('patient_id')
    # def _compute_display_name(self):
    #     print(self._context)


