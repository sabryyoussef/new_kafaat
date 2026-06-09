{
    'name': 'Edafaa Student Profile',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Student profile enhancements for Edafaa / OpenEduCat SIS',
    'depends': [
        'openeducat_core',
        'openeducat_parent',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/course_sequence.xml',
        'data/program_sequence.xml',
        'views/skill_views.xml',
        'views/course_views.xml',
        'views/program_views.xml',
        'views/student_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
