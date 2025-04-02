from odoo import fields, models

class LibraryBorrower(models.Model):
    _name = "library.borrower"
    _description = "Borrower"

    name = fields.Char(string="Name", required=True)
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    address = fields.Text(string="Address")
    member_since = fields.Date(string="Member Since")
    active = fields.Boolean(string="Active")
