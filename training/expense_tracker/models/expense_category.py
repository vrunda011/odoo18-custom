# -*- coding: utf-8 -*-

from odoo import fields, models

class ExpenseCategory(models.Model):
    _name = "expense.category"
    _description = "Expense Category"

    name = fields.Char("Category name")
    category_expense_ids = fields.One2many("expense.tracker", "category_id", string="Category Expenses")
