{
    'name': 'Bista DMS',
    'summary': """Document Management System""",
    "description": """Manages Documents""",
    "author": "Bista Solutions Pvt.Ltd",
    "version": "18.0",
    "depends": ['base','product', 'sale', 'stock'],
    "data": [
        'security/ir.model.access.csv',
        'views/dms_documents_views.xml',
        'views/dms_doc_tag_master_views.xml',
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
    ],
    'application' : True
}