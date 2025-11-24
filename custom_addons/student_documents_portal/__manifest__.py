# -*- coding: utf-8 -*-
{
    'name': 'Student Documents Portal',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Unified document management system with admin and student portal access',
    'description': """
        Student Documents Portal
        ========================
        
        A unified document management system with TWO workflows:
        
        1. Admin-Initiated Requests (gr.document.request):
           - Academy requests documents FROM students
           - Track required documents with deadlines
           - Manage compliance and enrollment requirements
           - Priority and mandatory document tracking
        
        2. Student-Initiated Requests (gr.document.request.portal):
           - Students upload documents proactively
           - Students request academy-issued documents
           - Self-service portal at /my/documents
           - Track request status in real-time
        
        Features:
        - Complete document lifecycle management
        - Email notifications at each stage
        - Admin review and approval workflows
        - Document download for students
        - Full audit trail via chatter
        
        This module depends on and integrates with Grants Training Suite V19.
    """,
    'author': 'Edafa',
    'website': 'https://www.edafa.sa',
    'license': 'OEEL-1',
    'depends': [
        'grants_training_suite_v19',
        'portal',
        'website',
        'mail',
        'documents',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/security_rules.xml',
        
        # Data
        'data/email_templates.xml',
        
        # Views
        'views/document_request_views.xml',  # Admin-initiated document requests
        'views/document_request_portal_views.xml',  # Student-initiated document requests
        'views/portal_templates.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

