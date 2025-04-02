{
    'name': 'Library Management',
    'summary': """Library Management System""",
    'description': """This app will help to track books""",
    'author': 'Bista Solutions',
    'version': "18.0",
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_cron.xml',
        'views/book_view.xml',
        'views/borrower_view.xml',
        'views/rental_view.xml',

    ],
}