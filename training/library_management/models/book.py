from odoo import fields, models, api


BOOK_TYPE = [('fiction', 'Fiction'),
             ('non-fiction', 'Non-Fiction'),
             ('science', 'Science'),
             ('history', 'History'),
             ('biography', 'Biography')]

class LibraryBook(models.Model):
    _name = "library.book"
    _description = "Book"

    name = fields.Char(string='Title', required=True)
    author_id = fields.Many2one('res.partner', string='Author')
    category = fields.Selection(BOOK_TYPE, string='Type')
    published_date = fields.Date(string='Published Date')
    copies = fields.Integer(string='Total Copies', default=1)
    book_code = fields.Char(string="Reference Number", readonly=True, default="New")
    rental_ids = fields.One2many('library.rental', 'book_id', string='Rentals')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(LibraryBook, self).create(vals_list)
        for record in res:
            record.book_code = self.env['ir.sequence'].next_by_code('library.book')
        return res

    # @api.depends('copies','rental_ids')
    # def _compute_state(self):
    #     for book in self:
    #         rented_copies = len(book.rental_ids.filtered(lambda r: r.state == 'rented')) #Corrected filter
    #
    #         if rented_copies == book.copies:
    #             book.state = 'borrowed'
    #         else:
    #             book.state = 'available'


