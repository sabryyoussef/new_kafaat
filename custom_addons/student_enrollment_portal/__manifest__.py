# -*- coding: utf-8 -*-
{
    'name': 'Student Enrollment Portal',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Complete student enrollment system with portal registration and multi-step review',
    'description': """
        Student Enrollment Portal
        =========================
        
        A comprehensive student enrollment system that provides:
        - Public portal registration for students
        - Multi-step review process (Eligibility → Documents → Approval)
        - Document management and verification
        - Automated student record creation
        - Portal user creation with login credentials
        - Course enrollment workflow
        - Email notifications at each stage
        - Full audit trail via chatter
        
        This module integrates with Grants Training Suite V19 for student and course management.
    """,
    'author': 'Edafa',
    'website': 'https://www.edafa.sa',
    'license': 'OEEL-1',
    'depends': [
        'grants_training_suite_v19',
        'portal',
        'website',
        'mail',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/security_rules.xml',
        
        # Data
        'data/sequences.xml',
        'data/email_templates.xml',
        
        # Views
        'views/student_registration_views.xml',
        'views/portal_templates.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

