{
    'name': 'Sale RMA',
    'summary': """Custom sale RMA odule""",
    "description": """""",
    "author": "Bista Solutions Pvt.Ltd",
    "version": "18.0",
    "depends": ['base','sale'],
    "data": [
        'security/ir.model.access.csv',
        # 'data/ir_sequence.xml',
        'views/sale_rma_view.xml',
        'views/rma_team_view.xml',
        'wizards/rma_wizard_view.xml',
    ],
}