# -*- coding: utf-8 -*-

from odoo import fields, models

class ExpenseTracker(models.Model):
    _name = "expense.budget"
    _description = "Expense Budget"

    name = fields.Char(string="Budget Name", required=True)
    month = fields.Selection([
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
    ], string="Month")

    year = fields.Integer(string="Year")
    category_id = fields.Many2one('expense.category', string="Category", required=True)
    budget_limit = fields.Float(string="Budget Limit", required=True)
    transaction_ids = fields.One2many('expense.tracker', 'budget_id', string="Transactions")
