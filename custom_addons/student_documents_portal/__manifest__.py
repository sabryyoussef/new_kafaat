# -*- coding: utf-8 -*-
{
    'name': 'Student Documents Portal',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Unified document management system with admin and student portal access',
    'description': """
        Student Documents Portal
        ========================
        
        A unified document management system with THREE workflows:
        
        1. Registration Documents (gr.registration.document):
           - Documents submitted during student registration
           - Auto-created when registration forms are submitted
           - Mandatory documents (ID, certificates, photos)
           - Review and approval workflow
           - Integrated with student enrollment portal
        
        2. Admin-Initiated Requests (gr.document.request):
           - Academy requests documents FROM students
           - Track required documents with deadlines
           - Manage compliance and enrollment requirements
           - Priority and mandatory document tracking
        
        3. Student-Initiated Requests (gr.document.request.portal):
           - Students upload documents proactively
           - Students request academy-issued documents
           - Self-service portal at /my/documents
           - Track request status in real-time
        
        Features:
        - **Complete document lifecycle management**
        - **Unified backend for all document types**
        - Email notifications at each stage
        - Admin review and approval workflows
        - Document download for students
        - Full audit trail via chatter
        - Automatic document request creation
        - Integrated with student registration workflow
        
        This module consolidates ALL document management for the academy.
    """,
    'author': 'Edafa',
    'website': 'https://www.edafa.sa',
    'license': 'OEEL-1',
    'depends': [
        'grants_training_suite_v19',
        'student_enrollment_portal',  # For registration document management
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
        'views/document_request_views.xml',  # Admin-initiated document requests
        'views/document_request_portal_views.xml',  # Student-initiated document requests
        'views/registration_document_views.xml',  # Registration document requests
        'views/student_registration_extension_views.xml',  # Extend student registration form
        'views/portal_templates.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

