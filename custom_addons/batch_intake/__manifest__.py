# -*- coding: utf-8 -*-
{
    'name': 'Batch Intake',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Batch intake management for training programs',
    'description': """
        Batch Intake Module
        ===================
        
        A module for managing batch intakes for training programs:
        - Batch creation and management
        - Student intake tracking
        - Batch status and progress monitoring
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'OEEL-1',
    'depends': [
        'base',
        'mail',
        'portal',
        'contacts',
        'openeducat_core',
    ],
    'data': [
        # Security
        'security/batch_intake_groups.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/sequence.xml',
        
        # Views
        'views/batch_intake_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'demo/batch_intake_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

