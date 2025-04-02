# -*- coding: utf-8 -*-

from odoo import fields, models

class ExpenseTracker(models.Model):
    _name = "expense.tracker"
    _description = "Expense Tracker"

    name = fields.Char("Name",required=True)
    date = fields.Date("Expense Date",required=True)
    amount = fields.Float("Amount", required=True, default=0.0)
    type = fields.Selection([('income','Income'), ('expense','Expense')], required=True, default='expense')
    currency_id = fields.Many2one('res.currency', string="Currency")
    budget_id = fields.Many2one('expense.budget', string="Budget", required=True)
    category_id = fields.Many2one('expense.category', string="Category")
    expense_line_ids = fields.One2many('expense.line', 'expense_id', string="Expense Lines")
    payment_method = fields.Selection([
        ('cash','Cash'),
        ('upi','UPI'),
        ('credit_card','Credit Card')
    ], string="Payment Method", required=True)

    users_ids = fields.Many2many('res.users', 'user_res_users_rel', 'user_id', 'res_users_id', string="Users")
    managers_ids = fields.Many2many('res.users', 'user_res_managers_rel', 'user_id', 'res_users_id', string="Managers")

    def action_quick_expense_wizard(self):
        view_id = self.env.ref('expense_tracker.expense_quick_wizard_wizard').id
        print("view_id", view_id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quick Expense',
            'res_model': 'expense.quick.wizard',
            'view_id': view_id,
            'view_mode': 'form',
            'target': 'new',
        }