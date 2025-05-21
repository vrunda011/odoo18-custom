{
    'name': 'Custom Sales',
    'summary': """Custom sale module""",
    "description": """""",
    "author": "Bista Solutions Pvt.Ltd",
    "version": "18.0",
    "depends": ['base','product','sale','contacts','purchase', 'stock'],
    "data": [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/res_partner_view.xml',
        'views/product_template_view.xml',
        'wizards/update_qty_wizard.xml',
        'views/report.xml',
        'views/custom_sale_order_template.xml',
        'views/purchase_order_view.xml',
        'views/product_pricelist_view.xml',
    ],
}