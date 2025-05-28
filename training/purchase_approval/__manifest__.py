{
    'name': 'PO Approval',
    'summary': """Custom purchase approval""",
    "description": """""",
    "author": "Bista Solutions Pvt.Ltd",
    "license": 'LGPL-3',
    "version": "18.0",
    "depends": ['base','purchase','mail'],
    "data": [
        'security/purchase_security.xml',
        'data/email_template.xml',
        'views/purchase_views.xml',
    ],
}