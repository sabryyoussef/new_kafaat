# -*- coding: utf-8 -*-
{
    'name': 'Batch Intake Processor',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Bulk student intake processing with Excel/CSV upload and eligibility validation',
    'description': """
        Batch Intake Processor
        ======================
        
        A standalone module for processing student intake applications in bulk.
        
        Features:
        - Upload student data via Excel (.xlsx, .xls) or CSV files
        - Automatic parsing and validation of uploaded data
        - Configurable eligibility criteria
        - Automatic categorization: Eligible / Not Eligible
        - Detailed validation reports with reasons
        - Export results to Excel/CSV
        - Batch processing with progress tracking
        - Error handling and logging
        
        Workflow:
        1. Upload Excel/CSV file with student data
        2. System validates data format and required fields
        3. Apply eligibility criteria automatically
        4. Review results (eligible/not eligible with reasons)
        5. Export processed results
        
        No dependencies on other custom modules - completely standalone!
    """,
    'author': 'Edafa',
    'website': 'https://www.edafa.sa',
    'license': 'OEEL-1',
    'depends': [
        'base',
        'mail',
    ],
    'external_dependencies': {
        'python': ['openpyxl', 'xlrd'],
    },
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/sequences.xml',
        
        # Views
        'views/batch_intake_views.xml',
        'views/applicant_views.xml',
        'views/eligibility_criteria_views.xml',
        'views/menu_views.xml',
        
        # Wizards
        'wizard/batch_upload_wizard_views.xml',
        'wizard/export_results_wizard_views.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

