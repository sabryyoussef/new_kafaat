# -*- coding: utf-8 -*-
{
    'name': 'Student Documents Portal',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Student document management with portal access',
    'description': """
        Student Documents Portal
        ========================
        
        A dedicated module for managing student documents with portal functionality:
        - Document request submission from portal
        - Document upload and verification
        - Document status tracking
        - Document download for students
        - Admin review and approval workflow
        
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
        'views/document_request_portal_views.xml',
        'views/portal_templates.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

