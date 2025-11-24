# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BatchUploadWizard(models.TransientModel):
    """
    Wizard for uploading batch intake files.
    """
    _name = 'batch.intake.upload.wizard'
    _description = 'Batch Upload Wizard'
    
    file_data = fields.Binary(
        string='Upload File',
        required=True,
        help='Upload Excel (.xlsx, .xls) or CSV file'
    )
    
    file_name = fields.Char(
        string='File Name',
        required=True
    )
    
    intake_date = fields.Date(
        string='Intake Date',
        default=fields.Date.context_today,
        required=True
    )
    
    description = fields.Text(
        string='Description'
    )
    
    def action_upload_and_process(self):
        """Create batch and process immediately"""
        self.ensure_one()
        
        # Create batch intake record
        batch = self.env['batch.intake'].create({
            'intake_date': self.intake_date,
            'description': self.description,
            'file_data': self.file_data,
            'file_name': self.file_name,
        })
        
        # Process the file
        return batch.action_process_file()
    
    def action_upload_only(self):
        """Create batch without processing"""
        self.ensure_one()
        
        batch = self.env['batch.intake'].create({
            'intake_date': self.intake_date,
            'description': self.description,
            'file_data': self.file_data,
            'file_name': self.file_name,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Batch Intake'),
            'res_model': 'batch.intake',
            'res_id': batch.id,
            'view_mode': 'form',
            'target': 'current',
        }

