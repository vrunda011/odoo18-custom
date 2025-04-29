{
    'name': 'Custom CRM',
    'summary': """Custom CRM module""",
    "description": """""",
    "author": "Bista Solutions Pvt.Ltd",
    "version": "18.0",
    "depends": ['base','crm','sale_crm'],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/stages_data.xml',
        'views/crm_lead_views.xml',
        'views/crm_percentage_stage_views.xml',
        'views/crm_student_activity_views.xml',
        'views/crm_menu_views.xml',

    ],
    'application' : True
}