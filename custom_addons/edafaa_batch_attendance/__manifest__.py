{
    'name': 'Edafaa Batch Attendance QR',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Stable QR per batch with portal student check-in into OpenEduCat attendance',
    'depends': [
        'openeducat_attendance',
        'openeducat_core',
        'portal',
        'website',
        'student_enrollment_portal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/op_batch_views.xml',
        'views/checkin_log_views.xml',
        'views/attendance_checkin_templates.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
