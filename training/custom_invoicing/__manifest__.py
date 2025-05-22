{
    'name': 'Custom Invoicing',
    'summary': """Custom invoicing module""",
    "description": """""",
    "author": "Bista Solutions Pvt.Ltd",
    "version": "18.0",
    "depends": ['base', 'account'],
    "data": [
        'security/ir.model.access.csv',
        'views/account_payment_view.xml',
        'views/invoice_line_view.xml',
    ],
}