{
    'name': 'Custom Manufacturing',
    'summary': """Custom Manufacturing module""",
    "description": """Custom Manufacturing""",
    "author": "Bista Solutions Pvt.Ltd",
    "license": "LGPL-3",
    "version": "18.0",
    "depends": ['base', 'sale', 'mrp'],
    "data": [
        'security/ir.model.access.csv',
        'wizards/generate_serial_wizard_views.xml',
        'wizards/mo_report_wizard_views.xml',
        'views/product_views.xml',
        'views/production_views.xml',
    ],
}