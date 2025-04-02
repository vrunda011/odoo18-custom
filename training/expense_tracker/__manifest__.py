# -*- coding: utf-8 -*-

{
    "name": "Expense Tracker",
    "summary": """Track income, expenses, and budgets""",
    "version": "18.0",
    "license": "OEEL-1",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/expense_tracker_views.xml",
        "views/expense_category_views.xml",
        "views/expense_budget_views.xml",
        "views/expense_line_view.xml",
        "wizards/expense_quick_wizard.xml",
    ],
    'application': True,
    'installable': True,
}