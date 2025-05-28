from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import UserError

class LoanManagement(models.Model):
    _inherit = 'mail.thread'
    _name = 'loan.loan'
    _description = 'Loan Details'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Partner')
    loan_period = fields.Integer(string='Loan Tenure')
    pr_amount = fields.Float(string='Principal Amount')
    interest_amount = fields.Float(string='Interest Amount', compute='_compute_interest_amount', store=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='Closing Date', compute='_compute_end_date', store=True)
    emi_date = fields.Date(string='EMI Date')
    emi_amount = fields.Float(string='Monthly Amount', compute='_compute_emi_amount', store=True)

    rate_lines = fields.One2many('loan.rate', 'loan_id', string='Rates')
    emi_lines = fields.One2many('loan.emi', 'loan_id', string='EMIs')
    current_interest_rate = fields.Float(string='Current Rate', copy=False)
    invoice_count = fields.Integer(string="Invoices", compute='_compute_invoice_count', default=0)
    team_id = fields.Many2one('loan.team', string='Approval Team', copy=False)
    next_approver_ids = fields.Many2many('res.users', string='Next Approvers', copy=False)
    payment_ids = fields.One2many('loan.payment', 'loan_id', string='Pre Payments')
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id)

    approval_level_ids = fields.One2many('loan.approval.level','loan_id', string='Approval Levels')
    loan_status = fields.Selection([
                            ('draft', 'Draft'),
                            ('to_approve', 'To Approve'),
                            ('approved', 'Approved'),
                            ('rejected', 'Rejected')], string='Status', default="draft", copy=False)

    is_user_approver = fields.Boolean(string='Is Current User Approver', compute='_compute_is_user_approver')
    current_level = fields.Integer(string='Current Approval Level')
    bill_count = fields.Integer(string="Bills", compute='_compute_bill_count', default=0)

    @api.depends('next_approver_ids')
    def _compute_is_user_approver(self):
        for rec in self:
            rec.is_user_approver = self.env.user in rec.next_approver_ids

    @api.depends('start_date', 'loan_period')
    def _compute_end_date(self):
        for rec in self:
            if rec.start_date:
                rec.end_date = rec.start_date + relativedelta(months=rec.loan_period)

    @api.depends('pr_amount', 'loan_period', 'current_interest_rate', 'payment_ids', 'emi_lines')
    def _compute_emi_amount(self):
        for rec in self:
            if rec.pr_amount and rec.loan_period and rec.current_interest_rate:
                monthly_rate = rec.current_interest_rate / 1200

                paid_lines = rec.emi_lines.filtered(lambda l: l.status in ['paid', 'generated'])
                advance_paid = sum(rec.payment_ids.filtered(lambda p: p.payment_status == 'paid').mapped('amount'))
                principal_paid = sum(paid_lines.mapped('total_payment'))
                remaining_principal = rec.pr_amount - principal_paid - advance_paid
                remaining_months = rec.loan_period - len(paid_lines)

                if remaining_principal > 0 and remaining_months > 0:
                    rec.emi_amount = (remaining_principal * monthly_rate * (1 + monthly_rate) ** remaining_months) / \
                                     (((1 + monthly_rate) ** remaining_months) - 1)
                else:
                    rec.emi_amount = (rec.pr_amount * monthly_rate * (1 + monthly_rate) ** rec.loan_period) / (
                                ((1 + monthly_rate) ** rec.loan_period) - 1)

    # @api.depends('emi_amount', 'loan_period', 'pr_amount')
    # def _compute_interest_amount(self):
    #     for rec in self:
    #         if rec.emi_amount:
    #             rec.interest_amount = ((rec.emi_amount * rec.loan_period)- rec.pr_amount)

    @api.depends('emi_amount', 'loan_period', 'emi_lines', 'pr_amount', 'payment_ids')
    def _compute_interest_amount(self):
        for rec in self:
            if rec.emi_amount:
                paid_lines = rec.emi_lines.filtered(lambda l: l.status in ['paid', 'generated'])
                remaining_months = rec.loan_period - len(paid_lines)
                advance_paid = sum(rec.payment_ids.filtered(lambda p: p.payment_status == 'paid').mapped('amount'))
                principal_remaining = rec.pr_amount - sum(paid_lines.mapped('paid_amt')) - advance_paid
                total_emi = rec.emi_amount * remaining_months
                rec.interest_amount = total_emi - principal_remaining

    @api.depends('interest_amount')
    def _compute_total_amount(self):
        for rec in self:
            if rec.interest_amount:
                rec.total_amount = rec.pr_amount + rec.interest_amount

    def action_calculate_emi_lines(self):
        if self.emi_date and self.emi_amount and self.rate_lines and self.loan_period:
            paid_lines = self.emi_lines.filtered(lambda l: l.status in ['paid', 'generated'])
            pending_lines = self.emi_lines.filtered(lambda l: l.status == 'pending')

            pending_lines.unlink()

            principal_paid = sum(paid_lines.mapped('total_payment'))
            advance_paid = sum(self.payment_ids.filtered(lambda p: p.payment_status == 'paid').mapped('amount'))
            remaining_bal = self.pr_amount - principal_paid - advance_paid

            if paid_lines:
                last_paid = max(paid_lines, key=lambda l: l.date)
                emi_date = last_paid.date + relativedelta(months=1)
                # remaining_bal = self.pr_amount - sum(self.emi_lines.filtered(lambda l: l.status != 'pending').mapped('total_payment'))

            else:
                emi_date = self.emi_date
                # remaining_bal = self.pr_amount

            total_time = self.loan_period
            emi_amount = self.emi_amount
            interest = self.current_interest_rate
            remaining_months = total_time - len(paid_lines)
            lines = []

            for next_date in range(remaining_months):
                interest_amt = (remaining_bal * interest) / (100 * 12)
                principal_paid_amt = emi_amount - interest_amt
                remaining_bal -= principal_paid_amt

                lines.append((0, 0, ({
                    'date': emi_date,
                    'paid_amt': principal_paid_amt,
                    'int_charged': interest_amt,
                    'total_payment': emi_amount,
                    'balance': remaining_bal,
                    'loan_id': self.id
                })))

                emi_date = emi_date + relativedelta(months=1)

            self.emi_lines = lines

    def _send_payment_reminder_today(self):
        today = date.today()
        emi_line_ids = self.env['loan.emi'].search([('date', '=', today), ('loan_id.loan_status', '=', 'approved')])
        emi_product = self.env.ref('loan_management.loan_management_emi_product').id

        for line in emi_line_ids:
            invoice_vals = {
                'move_type': 'out_invoice',
                'invoice_date': today,
                'partner_id': line.loan_id.partner_id.id,
                'invoice_line_ids': [],
                'loan_id': line.loan_id.id
            }

            invoice = self.env['account.move'].create(invoice_vals)

            line_vals = {
                'product_id': emi_product,
                'quantity': 1,
                'price_unit': line.total_payment,
                'discount': 0.0,
                'tax_ids': [],
                'move_id': invoice.id,
            }
            line.env['account.move.line'].create(line_vals)
            invoice.action_post()
            line.status = 'generated'

            line.loan_id._send_mail_to_loan_partner()

    def _send_mail_to_loan_partner(self):
        template_id = self.env.ref('loan_management.email_template_loan_emi_reminder')
        if template_id:
            template_id.send_mail(self.id, force_send=True)
        else:
            raise UserError("Mail Template not found. Please check the template.")

    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = self.env['account.move'].search_count([('loan_id', '=', record.id)])

    def action_open_invoice(self):
        form_view_id = self.env.ref('account.view_move_form').id
        list_view_id = self.env.ref('account.view_out_invoice_tree').id

        res = {
            'name': 'Invoice',
            'view_mode': 'form',
            'res_model': 'account.move',
            'view_id': form_view_id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

        if self.invoice_count >= 1:
            res['view_mode'] = 'list,form'
            res['views'] = [(list_view_id, 'list'), (form_view_id, 'form')]
            res['domain'] = ([('loan_id', '=', self.id)])
            res['view_id'] = False

        return res

    def action_confirm(self):
        self.loan_status = 'to_approve'
        level_lines = []
        level_lines = [(5, 0, 0)]
        for line in self.team_id.level_ids:
            level_lines.append((0, 0, {
                'level_no': line.level_no,
                'name': line.name,
                'user_ids': line.user_ids,
            }))
        self.approval_level_ids = level_lines

        if self.approval_level_ids:
            first_level = self.approval_level_ids.filtered(lambda l: l.level_no == 1)
            self.next_approver_ids = first_level.user_ids

        self.current_level = 1

    def button_approve(self):
        user = self.env.user

        if user in self.next_approver_ids:
            current_records = self.approval_level_ids.filtered(lambda l: l.level_no == self.current_level)
            current_records.stage = "approved"
            current_records.approved_by = user.name
            current_records.time = datetime.now()

            next_level_records = self.approval_level_ids.filtered(lambda l: l.level_no  ==self.current_level + 1)
            if next_level_records:
                next_level_records.stage = "to_approve"
                self.next_approver_ids = next_level_records.user_ids
                self.current_level += 1
            else:
                self.next_approver_ids = [(5, 0, 0)]
                self.loan_status = 'approved'

    def button_reject(self):
        user = self.env.user

        if user in self.next_approver_ids:
            current_records = self.approval_level_ids.filtered(lambda l: l.level_no == self.current_level)
            current_records.stage = "rejected"
            current_records.rejected_by = user.name
            current_records.time = datetime.now()

            next_levels = self.approval_level_ids.filtered(lambda l: l.level_no > self.current_level)
            for rec in next_levels:
                rec.stage = "rejected"

            self.next_approver_ids = [(5, 0, 0)]
            self.loan_status = 'rejected'

    def _compute_bill_count(self):
        for record in self:
            record.bill_count = self.env['account.move'].search_count([('loan_id', '=', record.id)])

    def action_open_bill(self):
        pass
        # form_view_id = self.env.ref('account.view_account_payment_form').id
        # list_view_id = self.env.ref('account.view_account_payment_tree').id
        #
        # res = {
        #     'name': 'Invoice',
        #     'view_mode': 'form',
        #     'res_model': 'account.payment',
        #     'view_id': form_view_id,
        #     'type': 'ir.actions.act_window',
        #     'target': 'current',
        # }
        #
        # # if self.bill_count >= 1:
        # #     res['view_mode'] = 'list,form'
        # #     res['views'] = [(list_view_id, 'list'), (form_view_id, 'form')]
        # #     res['domain'] = ([('loan_id', '=', self.id)])
        # #     res['view_id'] = False
        #
        # return res

