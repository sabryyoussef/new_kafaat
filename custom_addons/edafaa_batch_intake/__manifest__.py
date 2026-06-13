{
    'name': 'Edafaa Batch Intake Bridge',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Integrates Batch Intake into Edafaa/Kafaat student workflow',
    'depends': [
        'batch_intake',
        'edafaa_student_profile',
        'openeducat_core',
    ],
    'data': [
        'views/menu_views.xml',
        'views/student_views.xml',
        'views/batch_intake_views.xml',
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
