{
    'name': 'Edafaa Training CRM Enhancements',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'CRM lead targets, student bridge, and op.program training enhancements',
    'depends': [
        'crm',
        'sale',
        'openeducat_core',
        'edafaa_student_profile',
    ],
    'data': [
        'views/crm_team_views.xml',
        'views/crm_menu_views.xml',
        'views/res_partner_views.xml',
        'views/op_program_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
