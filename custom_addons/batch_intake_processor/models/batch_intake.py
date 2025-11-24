# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class BatchIntake(models.Model):
    """
    Main model for batch intake processing.
    Manages uploaded files and processing status.
    """
    _name = 'batch.intake'
    _description = 'Batch Intake Processing'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    name = fields.Char(
        string='Batch Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    
    intake_date = fields.Date(
        string='Intake Date',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    
    description = fields.Text(
        string='Description',
        help='Brief description of this intake batch'
    )
    
    # File Upload
    file_data = fields.Binary(
        string='Upload File',
        required=True,
        attachment=True,
        help='Upload Excel (.xlsx, .xls) or CSV file with applicant data'
    )
    
    file_name = fields.Char(
        string='File Name'
    )
    
    file_type = fields.Selection([
        ('xlsx', 'Excel (.xlsx)'),
        ('xls', 'Excel (.xls)'),
        ('csv', 'CSV')
    ], string='File Type', compute='_compute_file_type', store=True)
    
    # Processing Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('uploaded', 'File Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error')
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Statistics
    applicant_ids = fields.One2many(
        'batch.intake.applicant',
        'batch_id',
        string='Applicants'
    )
    
    total_count = fields.Integer(
        string='Total Applicants',
        compute='_compute_statistics',
        store=True
    )
    
    eligible_count = fields.Integer(
        string='Eligible',
        compute='_compute_statistics',
        store=True
    )
    
    not_eligible_count = fields.Integer(
        string='Not Eligible',
        compute='_compute_statistics',
        store=True
    )
    
    pending_count = fields.Integer(
        string='Pending Review',
        compute='_compute_statistics',
        store=True
    )
    
    error_count = fields.Integer(
        string='Errors',
        compute='_compute_statistics',
        store=True
    )
    
    eligibility_rate = fields.Float(
        string='Eligibility Rate (%)',
        compute='_compute_statistics',
        store=True
    )
    
    # Processing Info
    processed_date = fields.Datetime(
        string='Processed Date',
        readonly=True
    )
    
    processed_by_id = fields.Many2one(
        'res.users',
        string='Processed By',
        readonly=True
    )
    
    processing_notes = fields.Text(
        string='Processing Notes',
        readonly=True
    )
    
    error_log = fields.Text(
        string='Error Log',
        readonly=True
    )
    
    @api.depends('file_name')
    def _compute_file_type(self):
        """Determine file type from filename"""
        for record in self:
            if record.file_name:
                if record.file_name.endswith('.xlsx'):
                    record.file_type = 'xlsx'
                elif record.file_name.endswith('.xls'):
                    record.file_type = 'xls'
                elif record.file_name.endswith('.csv'):
                    record.file_type = 'csv'
                else:
                    record.file_type = False
            else:
                record.file_type = False
    
    @api.depends('applicant_ids.eligibility_status')
    def _compute_statistics(self):
        """Calculate statistics"""
        for record in self:
            total = len(record.applicant_ids)
            eligible = len(record.applicant_ids.filtered(lambda a: a.eligibility_status == 'eligible'))
            not_eligible = len(record.applicant_ids.filtered(lambda a: a.eligibility_status == 'not_eligible'))
            pending = len(record.applicant_ids.filtered(lambda a: a.eligibility_status == 'pending'))
            error = len(record.applicant_ids.filtered(lambda a: a.eligibility_status == 'error'))
            
            record.total_count = total
            record.eligible_count = eligible
            record.not_eligible_count = not_eligible
            record.pending_count = pending
            record.error_count = error
            record.eligibility_rate = (eligible / total * 100) if total > 0 else 0.0
    
    @api.model_create_multi
    def create(self, vals_list):
        """Generate sequence on creation"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('batch.intake') or _('New')
            if vals.get('file_data'):
                vals['state'] = 'uploaded'
        return super(BatchIntake, self).create(vals_list)
    
    def action_process_file(self):
        """Process uploaded file"""
        self.ensure_one()
        
        if not self.file_data:
            raise UserError(_('Please upload a file first.'))
        
        if self.file_type not in ['xlsx', 'xls', 'csv']:
            raise UserError(_('Invalid file type. Please upload Excel (.xlsx, .xls) or CSV file.'))
        
        self.write({'state': 'processing'})
        
        try:
            # Parse file and create applicants
            self._parse_and_create_applicants()
            
            # Apply eligibility criteria
            self._apply_eligibility_criteria()
            
            self.write({
                'state': 'completed',
                'processed_date': fields.Datetime.now(),
                'processed_by_id': self.env.user.id,
                'processing_notes': _('Successfully processed %d applicants') % self.total_count
            })
            
            self.message_post(
                body=_('Batch processing completed. %d eligible, %d not eligible out of %d total applicants.') % 
                     (self.eligible_count, self.not_eligible_count, self.total_count),
                message_type='notification'
            )
            
            _logger.info(f'Batch {self.name} processed successfully: {self.total_count} applicants')
            
        except Exception as e:
            error_msg = str(e)
            self.write({
                'state': 'error',
                'error_log': error_msg
            })
            self.message_post(
                body=_('Error processing batch: %s') % error_msg,
                message_type='notification'
            )
            _logger.error(f'Error processing batch {self.name}: {error_msg}')
            raise UserError(_('Error processing file: %s') % error_msg)
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Processing Results'),
            'res_model': 'batch.intake.applicant',
            'view_mode': 'list,form',
            'domain': [('batch_id', '=', self.id)],
            'context': {'default_batch_id': self.id}
        }
    
    def _parse_and_create_applicants(self):
        """Parse file and create applicant records"""
        self.ensure_one()
        
        import base64
        import io
        
        file_content = base64.b64decode(self.file_data)
        
        if self.file_type in ['xlsx', 'xls']:
            applicants_data = self._parse_excel(file_content)
        else:
            applicants_data = self._parse_csv(file_content)
        
        # Create applicant records
        for data in applicants_data:
            data['batch_id'] = self.id
            self.env['batch.intake.applicant'].create(data)
    
    def _parse_excel(self, file_content):
        """Parse Excel file"""
        import openpyxl
        import io
        
        applicants = []
        workbook = openpyxl.load_workbook(io.BytesIO(file_content))
        sheet = workbook.active
        
        # Get headers from first row
        headers = []
        for cell in sheet[1]:
            headers.append(str(cell.value).lower().strip() if cell.value else '')
        
        # Parse data rows
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            try:
                applicant_data = self._parse_row(headers, row, row_num)
                if applicant_data:
                    applicants.append(applicant_data)
            except Exception as e:
                _logger.warning(f'Error parsing row {row_num}: {e}')
                # Create error record
                applicants.append({
                    'name': f'Row {row_num}',
                    'eligibility_status': 'error',
                    'validation_notes': f'Error parsing row: {str(e)}'
                })
        
        return applicants
    
    def _parse_csv(self, file_content):
        """Parse CSV file"""
        import csv
        import io
        
        applicants = []
        csv_file = io.StringIO(file_content.decode('utf-8'))
        reader = csv.DictReader(csv_file)
        
        # Normalize headers
        headers = [h.lower().strip() for h in reader.fieldnames] if reader.fieldnames else []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # Convert row keys to lowercase
                normalized_row = {k.lower().strip(): v for k, v in row.items()}
                applicant_data = self._parse_row(headers, list(normalized_row.values()), row_num)
                if applicant_data:
                    applicants.append(applicant_data)
            except Exception as e:
                _logger.warning(f'Error parsing row {row_num}: {e}')
                applicants.append({
                    'name': f'Row {row_num}',
                    'eligibility_status': 'error',
                    'validation_notes': f'Error parsing row: {str(e)}'
                })
        
        return applicants
    
    def _parse_row(self, headers, row_values, row_num):
        """Parse a single row into applicant data"""
        # Expected column mappings
        column_map = {
            'name': ['name', 'full name', 'student name', 'applicant name'],
            'email': ['email', 'e-mail', 'email address'],
            'phone': ['phone', 'mobile', 'contact', 'phone number'],
            'age': ['age'],
            'education_level': ['education', 'education level', 'qualification'],
            'gpa': ['gpa', 'grade', 'marks'],
            'nationality': ['nationality', 'country'],
            'english_level': ['english', 'english level'],
        }
        
        data = {}
        
        # Map columns
        for field, possible_names in column_map.items():
            for col_name in possible_names:
                if col_name in headers:
                    idx = headers.index(col_name)
                    if idx < len(row_values):
                        value = row_values[idx]
                        if value is not None and str(value).strip():
                            data[field] = str(value).strip()
                            break
        
        # Validate required fields
        if not data.get('name'):
            raise ValueError('Name is required')
        
        return data
    
    def _apply_eligibility_criteria(self):
        """Apply eligibility criteria to all applicants"""
        self.ensure_one()
        
        criteria = self.env['batch.intake.eligibility.criteria'].search([], limit=1)
        
        for applicant in self.applicant_ids:
            if applicant.eligibility_status != 'error':
                applicant.check_eligibility(criteria)
    
    def action_view_applicants(self):
        """View all applicants"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Applicants'),
            'res_model': 'batch.intake.applicant',
            'view_mode': 'list,form',
            'domain': [('batch_id', '=', self.id)],
            'context': {'default_batch_id': self.id}
        }
    
    def action_export_results(self):
        """Open export wizard"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Export Results'),
            'res_model': 'batch.intake.export.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_batch_id': self.id}
        }
    
    def action_reset_to_draft(self):
        """Reset to draft and clear applicants"""
        for record in self:
            record.applicant_ids.unlink()
            record.write({
                'state': 'draft',
                'processed_date': False,
                'processed_by_id': False,
                'processing_notes': False,
                'error_log': False
            })

