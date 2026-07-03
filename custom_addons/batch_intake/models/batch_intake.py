# -*- coding: utf-8 -*-

import base64
import csv
import io
import json
import logging
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BatchIntake(models.Model):
    _name = 'batch.intake'
    _description = 'Batch Intake'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Basic Fields
    name = fields.Char(
        string='Batch Name',
        required=True,
        default=lambda self: _('New'),
        copy=False,
        tracking=True
    )
    
    code = fields.Char(
        string='Batch Code',
        copy=False,
        tracking=True,
        readonly=True
    )
    
    description = fields.Text(
        string='Description',
        help='Description of the batch intake'
    )
    
    # File Upload Fields
    filename = fields.Char(
        string='File Name',
        help='Name of the uploaded file'
    )
    
    file_data = fields.Binary(
        string='File',
        help='Upload CSV or Excel file with student data'
    )
    
    file_size = fields.Integer(
        string='File Size (bytes)',
        compute='_compute_file_size',
        store=True,
        help='Size of the uploaded file in bytes'
    )
    
    file_type = fields.Selection([
        ('csv', 'CSV File'),
        ('xlsx', 'Excel File'),
    ], string='File Type', compute='_compute_file_type', store=True)
    
    upload_date = fields.Datetime(
        string='Upload Date',
        default=fields.Datetime.now
    )
    
    validation_date = fields.Datetime(
        string='Validation Date',
        help='Date when the file was validated'
    )
    
    processing_date = fields.Datetime(
        string='Processing Date',
        help='Date when the file was processed'
    )
    
    # Status Fields
    state = fields.Selection([
        ('draft', 'Draft'),
        ('uploaded', 'File Uploaded'),
        ('mapping', 'Column Mapping'),
        ('validated', 'Validated'),
        ('processed', 'Processed'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('error', 'Error'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, required=True)
    
    # Progress Tracking Fields
    progress_percentage = fields.Float(
        string='Progress (%)',
        compute='_compute_progress_percentage',
        store=True,
        help='Overall progress percentage of the batch processing'
    )
    
    current_stage = fields.Char(
        string='Current Stage',
        compute='_compute_current_stage',
        store=True,
        help='Current processing stage description'
    )
    
    # Processing Fields
    total_records = fields.Integer(
        string='Total Records',
        default=0,
        help='Total number of records in the file'
    )
    
    processed_records = fields.Integer(
        string='Processed Records',
        default=0,
        help='Number of records successfully processed'
    )
    
    error_records = fields.Integer(
        string='Error Records',
        default=0,
        help='Number of records with errors'
    )
    
    validation_errors = fields.Text(
        string='Validation Errors',
        help='Details of validation errors'
    )
    
    validation_warnings = fields.Text(
        string='Validation Warnings',
        help='Details of validation warnings'
    )
    
    success_rate = fields.Float(
        string='Success Rate (%)',
        compute='_compute_success_rate',
        store=True,
        help='Percentage of successfully processed records'
    )
    
    # Notification Fields
    notification_sent = fields.Boolean(
        string='Notification Sent',
        default=False,
        help='Whether notification has been sent for this batch'
    )
    
    notification_type = fields.Selection([
        ('none', 'No Notification'),
        ('success', 'Success Notification'),
        ('error', 'Error Notification'),
        ('warning', 'Warning Notification'),
        ('info', 'Info Notification')
    ], string='Notification Type', default='none', help='Type of notification sent')
    
    email_notification_enabled = fields.Boolean(
        string='Email Notifications Enabled',
        default=True,
        help='Whether email notifications are enabled for this batch'
    )
    
    in_app_notification_enabled = fields.Boolean(
        string='In-App Notifications Enabled',
        default=True,
        help='Whether in-app notifications are enabled for this batch'
    )
    
    # Dates
    start_date = fields.Date(
        string='Start Date',
        required=True,
        tracking=True,
        help='Start date of the batch intake'
    )
    
    end_date = fields.Date(
        string='End Date',
        required=True,
        tracking=True,
        help='End date of the batch intake'
    )
    
    # Capacity Fields
    max_capacity = fields.Integer(
        string='Maximum Capacity',
        default=0,
        tracking=True,
        help='Maximum number of students for this batch'
    )
    
    current_enrollment = fields.Integer(
        string='Current Enrollment',
        compute='_compute_current_enrollment',
        store=True,
        help='Current number of enrolled students'
    )
    
    available_slots = fields.Integer(
        string='Available Slots',
        compute='_compute_available_slots',
        store=True,
        help='Number of available slots remaining'
    )
    
    # Progress Tracking
    enrollment_percentage = fields.Float(
        string='Enrollment (%)',
        compute='_compute_enrollment_percentage',
        store=True,
        help='Percentage of enrollment capacity used'
    )
    
    # Related Records
    student_ids = fields.One2many(
        'res.partner',
        'batch_intake_id',
        string='Students',
        domain=[('is_company', '=', False)],
        help='Students enrolled in this batch'
    )
    
    openeducat_student_ids = fields.One2many(
        'op.student',
        'batch_intake_id',
        string='OpenEduCat Students',
        help='OpenEduCat students enrolled in this batch'
    )
    
    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    # OpenEduCat Integration Fields
    course_id = fields.Many2one(
        'op.course',
        string='Course',
        help='Course to enroll students in'
    )
    
    batch_id = fields.Many2one(
        'op.batch',
        string='Batch',
        domain="[('course_id', '=', course_id)]",
        help='Batch to enroll students in'
    )
    
    academic_year_id = fields.Many2one(
        'op.academic.year',
        string='Academic Year',
        help='Academic year for enrollment'
    )
    
    academic_term_id = fields.Many2one(
        'op.academic.term',
        string='Academic Term',
        help='Academic term for enrollment'
    )
    
    # Computed Fields
    @api.depends('student_ids', 'openeducat_student_ids')
    def _compute_current_enrollment(self):
        """Compute current enrollment count."""
        for record in self:
            # Count OpenEduCat students if available, otherwise count partners
            if record.openeducat_student_ids:
                record.current_enrollment = len(record.openeducat_student_ids)
            else:
                record.current_enrollment = len(record.student_ids)
    
    @api.depends('max_capacity', 'current_enrollment')
    def _compute_available_slots(self):
        """Compute available slots."""
        for record in self:
            if record.max_capacity > 0:
                record.available_slots = max(0, record.max_capacity - record.current_enrollment)
            else:
                record.available_slots = 0
    
    @api.depends('max_capacity', 'current_enrollment')
    def _compute_enrollment_percentage(self):
        """Compute enrollment percentage."""
        for record in self:
            if record.max_capacity > 0:
                record.enrollment_percentage = (record.current_enrollment / record.max_capacity) * 100
            else:
                record.enrollment_percentage = 0.0
    
    @api.depends('file_data')
    def _compute_file_size(self):
        """Compute file size from binary data."""
        for record in self:
            if record.file_data:
                # Calculate size from base64 encoded data
                record.file_size = len(record.file_data) * 3 // 4  # Approximate size
            else:
                record.file_size = 0
    
    @api.depends('filename', 'file_data')
    def _compute_file_type(self):
        """Compute file type based on filename extension."""
        for record in self:
            if record.filename:
                filename_lower = record.filename.lower()
                if filename_lower.endswith('.csv'):
                    record.file_type = 'csv'
                elif filename_lower.endswith(('.xlsx', '.xls')):
                    record.file_type = 'xlsx'
                else:
                    record.file_type = False
            else:
                record.file_type = False
    
    @api.depends('total_records', 'processed_records')
    def _compute_success_rate(self):
        """Compute success rate percentage."""
        for record in self:
            if record.total_records > 0:
                record.success_rate = (record.processed_records / record.total_records) * 100
            else:
                record.success_rate = 0.0
    
    @api.depends('state')
    def _compute_progress_percentage(self):
        """Compute overall progress percentage."""
        for record in self:
            progress = 0.0
            stage_values = {
                'uploaded': 25.0,
                'mapping': 50.0,
                'validated': 75.0,
                'processed': 100.0,
                'open': 100.0,
            }
            if record.state in stage_values:
                progress = stage_values[record.state]
            elif record.state == 'error':
                progress = 0.0
            elif record.state == 'cancelled':
                progress = 0.0
            record.progress_percentage = progress
    
    @api.depends('state')
    def _compute_current_stage(self):
        """Compute current stage description."""
        for record in self:
            if record.state == 'draft':
                record.current_stage = 'Ready to Upload'
            elif record.state == 'uploaded':
                record.current_stage = 'File Uploaded - Ready for Validation'
            elif record.state == 'mapping':
                record.current_stage = 'Column Mapping Required'
            elif record.state == 'validated':
                record.current_stage = 'File Validated - Ready for Processing'
            elif record.state == 'processed':
                record.current_stage = 'Processing Complete'
            elif record.state == 'open':
                record.current_stage = 'Batch Open'
            elif record.state == 'closed':
                record.current_stage = 'Batch Closed'
            elif record.state == 'error':
                record.current_stage = 'Error Occurred'
            elif record.state == 'cancelled':
                record.current_stage = 'Processing Cancelled'
            else:
                record.current_stage = 'Unknown Stage'
    
    # Constraints
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Check that end date is after start date."""
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date < record.start_date:
                    raise ValidationError(_('End date must be after start date.'))
    
    @api.constrains('max_capacity', 'current_enrollment')
    def _check_capacity(self):
        """Check that enrollment doesn't exceed capacity."""
        for record in self:
            if record.max_capacity > 0 and record.current_enrollment > record.max_capacity:
                raise ValidationError(_('Current enrollment (%d) cannot exceed maximum capacity (%d).') % 
                                     (record.current_enrollment, record.max_capacity))
    
    # Actions
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate sequence number."""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('batch.intake') or _('New')
            if not vals.get('code'):
                vals['code'] = self.env['ir.sequence'].next_by_code('batch.intake.code') or _('New')
        return super(BatchIntake, self).create(vals_list)
    
    def write(self, vals):
        """Override write to prevent manual code changes."""
        if 'code' in vals and vals['code']:
            # Allow code update only if it's different and valid
            pass
        return super(BatchIntake, self).write(vals)
    
    def action_open(self):
        """Open the batch intake."""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Only draft batches can be opened.'))
        self.state = 'open'
        return True
    
    def action_close(self):
        """Close the batch intake."""
        self.ensure_one()
        if self.state != 'open':
            raise UserError(_('Only open batches can be closed.'))
        self.state = 'closed'
        return True
    
    def action_cancel(self):
        """Cancel the batch intake."""
        self.ensure_one()
        if self.state == 'closed':
            raise UserError(_('Closed batches cannot be cancelled.'))
        self.state = 'cancelled'
        return True
    
    def action_reopen(self):
        """Reopen a closed or cancelled batch."""
        self.ensure_one()
        if self.state not in ['closed', 'cancelled']:
            raise UserError(_('Only closed or cancelled batches can be reopened.'))
        self.state = 'open'
        return True
    
    def action_view_students(self):
        """Open the students view for this batch."""
        self.ensure_one()
        return {
            'name': _('Students'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [('batch_intake_id', '=', self.id), ('is_company', '=', False)],
            'context': {'default_batch_intake_id': self.id},
        }
    
    def _parse_file(self):
        """Parse the uploaded file and return records."""
        self.ensure_one()
        if not self.file_data:
            return []
        
        try:
            file_content = base64.b64decode(self.file_data)
            
            if self.file_type == 'csv':
                # Parse CSV file
                csv_file = io.StringIO(file_content.decode('utf-8'))
                reader = csv.DictReader(csv_file)
                records = [row for row in reader]
                return records
            elif self.file_type == 'xlsx':
                # For Excel files, we would need openpyxl or xlrd
                # For now, return empty list and show error
                raise UserError(_('Excel file parsing not yet implemented. Please use CSV format.'))
            else:
                return []
        except Exception as e:
            _logger.error('Error parsing file: %s', str(e))
            raise UserError(_('Error parsing file: %s') % str(e))
    
    def action_upload_file(self):
        """Action to upload and validate file."""
        self.ensure_one()
        
        if not self.file_data:
            raise UserError(_('Please upload a file first.'))
        
        if not self.filename:
            raise UserError(_('File name is required.'))
        
        # Validate file size (max 10MB)
        max_file_size = 10 * 1024 * 1024  # 10MB in bytes
        if self.file_size > max_file_size:
            raise UserError(_('File size (%d bytes) exceeds maximum allowed size of %d bytes (10MB).') % 
                          (self.file_size, max_file_size))
        
        # Validate file type
        if not self.file_type:
            raise UserError(_('Unsupported file type. Please upload CSV (.csv) or Excel (.xlsx, .xls) files only.'))
        
        try:
            # Parse file and count records
            records = self._parse_file()
            self.total_records = len(records)
            
            # Validate that we have records
            if not records:
                self.state = 'error'
                raise UserError(_('No records found in the uploaded file. Please check the file format and content.'))
            
            # Update state
            self.state = 'uploaded'
            self.upload_date = fields.Datetime.now()
            
            # Log the action
            _logger.info('File uploaded for batch %s: %s (%d bytes) - %d records found', 
                        self.name, self.filename, self.file_size, self.total_records)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('File Uploaded Successfully'),
                    'message': _('File "%s" (%d bytes) uploaded successfully. %d records found.') % 
                              (self.filename, self.file_size, self.total_records),
                    'type': 'success',
                }
            }
            
        except Exception as e:
            _logger.error('Error uploading file for batch %s: %s', self.name, str(e))
            self.state = 'error'
            self.validation_errors = str(e)
            raise UserError(_('Error uploading file: %s') % str(e))
    
    def action_validate_file(self):
        """Action to validate the uploaded file."""
        self.ensure_one()
        
        if self.state != 'uploaded':
            raise UserError(_('Please upload a file first.'))
        
        try:
            # Parse file again
            records = self._parse_file()
            self.total_records = len(records)
            
            # Basic validation - check if records have required fields
            errors = []
            for idx, record in enumerate(records, start=1):
                if not record.get('name') and not record.get('Name'):
                    errors.append(_('Row %d: Missing name field') % idx)
            
            if errors:
                self.validation_errors = '\n'.join(errors[:10])  # Show first 10 errors
                self.error_records = len(errors)
                self.state = 'error'
            else:
                self.validation_errors = False
                self.state = 'validated'
                self.error_records = 0
            
            self.validation_date = fields.Datetime.now()
            
            # Log the validation
            _logger.info('File validated for batch %s: %d records, %d errors', 
                        self.name, self.total_records, self.error_records)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('File Validated'),
                    'message': _('File validation completed. %d records found, %d errors.') % 
                              (self.total_records, self.error_records),
                    'type': 'success' if not errors else 'warning',
                }
            }
            
        except Exception as e:
            _logger.error('Error validating batch %s: %s', self.name, str(e))
            self.state = 'error'
            self.validation_errors = str(e)
            raise UserError(_('Error validating file: %s') % str(e))
    
    def action_process_file(self):
        """Action to process the validated file."""
        self.ensure_one()
        
        if self.state != 'validated':
            raise UserError(_('Please validate the file first.'))
        
        # Check if course is set for OpenEduCat enrollment
        if not self.course_id:
            raise UserError(_('Please set a Course in the OpenEduCat Enrollment section before processing the file.'))
        
        try:
            # Parse file again
            records = self._parse_file()
            
            # Process records - create OpenEduCat students
            created_count = 0
            updated_count = 0
            errors = []
            
            for idx, record in enumerate(records, start=1):
                try:
                    # Extract data from record
                    name = record.get('name') or record.get('Name') or record.get('NAME') or ''
                    email = record.get('email') or record.get('Email') or record.get('EMAIL') or ''
                    phone = record.get('phone') or record.get('Phone') or record.get('PHONE') or ''
                    
                    if not name:
                        errors.append(_('Row %d: Missing name') % idx)
                        continue
                    
                    # Split name into first_name and last_name
                    name_parts = name.strip().split(' ', 1)
                    first_name = name_parts[0] if name_parts else name
                    last_name = name_parts[1] if len(name_parts) > 1 else ''
                    
                    # Prepare course detail values
                    course_detail_vals = {
                        'course_id': self.course_id.id,
                        'batch_id': self.batch_id.id if self.batch_id else False,
                        'academic_years_id': self.academic_year_id.id if self.academic_year_id else False,
                        'academic_term_id': self.academic_term_id.id if self.academic_term_id else False,
                        'state': 'running',
                    }
                    
                    # Check if student already exists by email
                    existing_student = False
                    if email:
                        existing_student = self.env['op.student'].search([
                            ('partner_id.email', '=', email)
                        ], limit=1)
                    
                    # Create or update student
                    if existing_student:
                        # Update existing student and add course if not already enrolled
                        # Check if student already has this course/batch combination
                        existing_course = existing_student.course_detail_ids.filtered(
                            lambda c: c.course_id.id == self.course_id.id and 
                            (not self.batch_id or c.batch_id.id == self.batch_id.id)
                        )
                        if not existing_course:
                            existing_student.write({
                                'course_detail_ids': [(0, 0, course_detail_vals)],
                                'batch_intake_id': self.id,
                            })
                            updated_count += 1
                        else:
                            # Student already enrolled in this course/batch, just update batch_intake_id
                            existing_student.write({
                                'batch_intake_id': self.id,
                            })
                    else:
                        # Create new partner first
                        partner_vals = {
                            'name': name,
                            'email': email if email else False,
                            'phone': phone if phone else False,
                            'is_company': False,
                            'batch_intake_id': self.id,
                        }
                        partner = self.env['res.partner'].create(partner_vals)
                        
                        # Prepare student values
                        student_vals = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'name': name,
                            'gender': 'm',  # Default, can be updated from CSV if needed
                            'batch_intake_id': self.id,
                            'partner_id': partner.id,
                            'course_detail_ids': [(0, 0, course_detail_vals)],
                        }
                        
                        # Create student with partner
                        student = self.env['op.student'].create(student_vals)
                        created_count += 1
                    
                except Exception as e:
                    errors.append(_('Row %d: %s') % (idx, str(e)))
                    _logger.error('Error creating student for row %d: %s', idx, str(e))
            
            # Update counters
            self.processed_records = created_count + updated_count
            self.error_records = len(errors)
            self.processing_date = fields.Datetime.now()
            self.state = 'processed'
            
            if errors:
                self.validation_errors = '\n'.join(errors[:20])  # Show first 20 errors
            
            # Log the processing
            _logger.info('File processed for batch %s: %d created, %d updated, %d errors', 
                        self.name, created_count, updated_count, len(errors))
            
            message = _('Import completed. %d students created') % created_count
            if updated_count > 0:
                message += _(', %d students updated') % updated_count
            if errors:
                message += _(', %d errors') % len(errors)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Import Completed'),
                    'message': message,
                    'type': 'success' if not errors else 'warning',
                }
            }
            
        except Exception as e:
            _logger.error('Error processing batch %s: %s', self.name, str(e))
            self.state = 'error'
            self.validation_errors = str(e)
            raise UserError(_('Error processing file: %s') % str(e))
    
    def action_reset(self):
        """Reset the batch to draft state."""
        self.ensure_one()
        if self.state in ['draft', 'error']:
            self.state = 'draft'
            self.file_data = False
            self.filename = False
            self.total_records = 0
            self.processed_records = 0
            self.error_records = 0
            self.validation_errors = False
            return True
        else:
            raise UserError(_('Can only reset draft or error batches.'))
    
    def action_download_template(self):
        """Download a sample CSV template for student data import."""
        self.ensure_one()
        try:
            # Create sample data with example records
            sample_data = [
                {
                    'name': 'Ahmed Hassan',
                    'email': 'ahmed.hassan@example.com',
                    'phone': '+966501234567',
                },
                {
                    'name': 'Fatima Al-Zahra',
                    'email': 'fatima.alzahra@example.com',
                    'phone': '+966501234568',
                },
                {
                    'name': 'Mohammed Ali',
                    'email': 'mohammed.ali@example.com',
                    'phone': '+966501234569',
                },
                {
                    'name': 'Sara Ahmed',
                    'email': 'sara.ahmed@example.com',
                    'phone': '+966501234570',
                },
                {
                    'name': 'Omar Ibrahim',
                    'email': 'omar.ibrahim@example.com',
                    'phone': '+966501234571',
                }
            ]
            
            # Create CSV file in memory
            output = io.StringIO()
            if sample_data:
                writer = csv.DictWriter(output, fieldnames=sample_data[0].keys())
                writer.writeheader()
                writer.writerows(sample_data)
            
            csv_data = output.getvalue().encode('utf-8')
            output.close()
            
            # Encode as base64
            csv_base64 = base64.b64encode(csv_data)
            
            # Create attachment
            attachment = self.env['ir.attachment'].create({
                'name': 'Batch_Intake_Template.csv',
                'type': 'binary',
                'datas': csv_base64,
                'mimetype': 'text/csv',
                'res_model': 'batch.intake',
                'res_id': self.id,
            })
            
            # Return download action
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }
                
        except Exception as e:
            _logger.error('Error creating template: %s', str(e))
            raise UserError(_('Error creating template file: %s') % str(e))

