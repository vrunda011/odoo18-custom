{
    'name': 'Bista HMS',
    'summary': """Hospital Management System""",
    "description": """this app will help to manage hospital""",
    "author": "Bista Solutions Pvt.Ltd",
    "version": "18.0",
    "depends": ['base','product','sale'],
    "data": [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_cron.xml',
        'views/res_patient_view.xml',
        'views/appointment_view.xml',
        'views/res_doctor_view.xml',
        'views/hospital_specialization_view.xml',
        'views/prescription_view.xml',
    ],
}