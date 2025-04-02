# -*- coding: utf-8 -*-

from odoo import fields, models

class ExpenseLine(models.Model):
    _name = "expense.line"
    _description = "Expense Line Item"

    name = fields.Char("Description", required=True)
    amount = fields.Float("Amount", required=True)
    category_id = fields.Many2one('expense.category', string="Category", required=True)
    expense_id = fields.Many2one('expense.tracker', string="Expense", ondelete='cascade')
