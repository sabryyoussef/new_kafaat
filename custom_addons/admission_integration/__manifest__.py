# -*- coding: utf-8 -*-
{
    'name': 'Admission Integration',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Unified admission system integrating multiple registration sources',
    'description': """
        Admission Integration
        =====================
        
        This module integrates all student registration sources into the 
        OpenEduCat Admission system:
        
        - Student Registration Portal integration
        - Batch Intake integration
        - Contact Pool Manager integration
        
        All eligible students from these sources appear in the unified 
        OpenEduCat admission tree view for centralized management.
        
        Features:
        - Source tracking for all admissions
        - Automatic sync from approved registrations
        - Manual sync from batch intakes and contact pools
        - Duplicate prevention
        - Bidirectional linking to source records
    """,
    'author': 'Edafa',
    'website': 'https://www.edafa.sa',
    'license': 'OEEL-1',
    'depends': [
        'openeducat_admission',
        'openeducat_core',
        'student_enrollment_portal',
        'batch_intake',
        'contact_pool_manager',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Views
        'views/admission_views.xml',
        'views/student_registration_views.xml',
        'views/batch_intake_views.xml',
        'views/contact_pool_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

