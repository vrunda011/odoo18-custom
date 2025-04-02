from odoo import fields, models

class ExpenseQuickWizard(models.TransientModel):
    _name = 'expense.quick.wizard'
    _description = 'Expense Quick Wizard'

    name = fields.Char("Name", required=True)
    date = fields.Date("Expense Date", required=True)
    amount = fields.Float("Amount", required=True, default=0.0)
    category_id = fields.Many2one('expense.category', string="Category")
