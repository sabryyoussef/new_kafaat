{
    'name': 'Edafaa Student Profile Portal Bridge',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Bridge student enrollment portal to Edafaa required op.student profile fields',
    'depends': [
        'edafaa_student_profile',
        'student_enrollment_portal',
    ],
    'data': [
        'views/student_registration_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
