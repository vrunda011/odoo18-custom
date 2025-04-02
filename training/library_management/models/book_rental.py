from datetime import date, timedelta

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class LibraryRental(models.Model):
    _name = "library.rental"
    _description = "Book Rental"
    _rec_name = "borrower_id"

    rental_code = fields.Char(string="Reference", readonly=True, default="New")
    borrower_id = fields.Many2one("library.borrower",string="Borrower Id", required=True)
    book_id = fields.Many2one("library.book", string="Book Id", required=True)
    rental_date = fields.Date(string="Rental Date", default=fields.Date.today)
    return_date = fields.Date(string="Return Date")
    state = fields.Selection([('borrowed', 'Borrowed'),
                              ('returned', 'Returned'),
                              ('overdue', 'Overdue')], string='Status')

    due_date = fields.Date(string="Due Date", compute="_compute_due_date", store=True)
    late_fee = fields.Integer(compute='_compute_late_fee', string="Late Fee")

    @api.constrains('book_id')
    def _check_availability(self):
        for rec in self:
            book = rec.book_id
            rented_copies = len(book.rental_ids.filtered(lambda r: r.state == 'rented'))
            if rented_copies >= book.copies:
                raise ValidationError("No available copies of this book!")

    @api.depends('rental_date')
    def _compute_due_date(self):
        for rec in self:
            rec.due_date = rec.rental_date + timedelta(days=14)

    @api.depends('return_date', 'due_date')
    def _compute_late_fee(self):
        for rec in self:
            if rec.return_date and rec.due_date and rec.return_date > rec.due_date:
                days_overdue = (rec.return_date - rec.due_date).days
                rec.late_fee = days_overdue * 5.0
            else:
                rec.late_fee = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        res = super(LibraryRental, self).create(vals_list)
        for record in res:
            record.rental_code = self.env['ir.sequence'].next_by_code('library.rental')
        return res

    def _move_books_to_overdue(self):
        overdue_date = date.today() - timedelta(days=14)

        books = self.env['library.rental'].search([
            ('state','=','borrowed'),
            ('rental_date','<=',overdue_date),
            ('return_date','=',False)
        ])

        for book in books:
            book.state='overdue'

