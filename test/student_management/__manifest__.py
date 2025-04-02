# -*- coding: utf-8 -*-

{
    'name': 'Student Management',
    'summary': 'Student Management System',
    "description": """This app will help to manage Student details.""",
    "author": "Bista Solutions Pvt.Ltd",
    "version": "18.0",
    "depends": ['base','product'],
    "data": [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_cron.xml',
        'views/student_student_view.xml',
        'views/student_subject_view.xml',
        'views/student_tuition_fee_view.xml',

    ],
}