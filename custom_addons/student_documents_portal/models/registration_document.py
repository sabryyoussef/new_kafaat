# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class RegistrationDocument(models.Model):
    """
    Document requests specifically for student registration process.
    These are documents required during the initial registration workflow.
    """
    _name = 'gr.registration.document'
    _description = 'Registration Document Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    # Basic Information
    name = fields.Char(
        string='Document Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    
    registration_id = fields.Many2one(
        'student.registration',
        string='Registration',
        required=True,
        ondelete='cascade',
        tracking=True,
        index=True
    )
    
    # Document Type - Registration specific
    document_type = fields.Selection([
        ('national_id', 'National ID / Iqama'),
        ('passport', 'Passport'),
        ('birth_certificate', 'Birth Certificate'),
        ('educational_certificate', 'Educational Certificate'),
        ('previous_training_certificate', 'Previous Training Certificate'),
        ('photo', 'Personal Photo'),
        ('other', 'Other Document')
    ], string='Document Type', required=True, tracking=True)
    
    document_name = fields.Char(
        string='Document Name',
        help='Specific name/description of the document',
        tracking=True
    )
    
    document_description = fields.Text(
        string='Description',
        help='Additional details or requirements for this document'
    )
    
    # Document Requirements
    is_mandatory = fields.Boolean(
        string='Mandatory',
        default=True,
        help='Whether this document is required for registration approval',
        tracking=True
    )
    
    required_format = fields.Char(
        string='Required Format',
        default='PDF, JPG, PNG',
        help='Accepted file formats'
    )
    
    max_file_size = fields.Integer(
        string='Max File Size (MB)',
        default=5,
        help='Maximum allowed file size in megabytes'
    )
    
    # Document Upload
    document_file = fields.Binary(
        string='Document File',
        attachment=True,
        tracking=True
    )
    
    document_filename = fields.Char(
        string='Filename'
    )
    
    # Workflow State
    state = fields.Selection([
        ('pending', 'Pending Upload'),
        ('uploaded', 'Uploaded'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected - Reupload Required')
    ], string='Status', default='pending', required=True, tracking=True)
    
    # Review Information
    review_notes = fields.Text(
        string='Review Notes',
        tracking=True
    )
    
    rejection_reason = fields.Text(
        string='Rejection Reason',
        help='Why was this document rejected',
        tracking=True
    )
    
    reviewed_by_id = fields.Many2one(
        'res.users',
        string='Reviewed By',
        tracking=True
    )
    
    review_date = fields.Datetime(
        string='Review Date',
        readonly=True,
        tracking=True
    )
    
    # Submission Information
    submitted_by_id = fields.Many2one(
        'res.users',
        string='Submitted By',
        readonly=True,
        tracking=True
    )
    
    submission_date = fields.Datetime(
        string='Submission Date',
        readonly=True,
        tracking=True
    )
    
    # Related fields from registration
    student_name = fields.Char(
        related='registration_id.student_name_english',
        string='Student Name',
        store=True,
        readonly=True
    )
    
    registration_state = fields.Selection(
        related='registration_id.state',
        string='Registration Status',
        store=True,
        readonly=True
    )
    
    # Computed Fields
    can_upload = fields.Boolean(
        string='Can Upload',
        compute='_compute_can_upload'
    )
    
    @api.depends('state', 'registration_id.state')
    def _compute_can_upload(self):
        """Determine if document can be uploaded based on state"""
        for record in self:
            # Can upload if pending or rejected, and registration not finalized
            record.can_upload = (
                record.state in ['pending', 'rejected'] and
                record.registration_id.state not in ['enrolled', 'rejected']
            )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Generate sequence number on creation"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('gr.registration.document') or _('New')
        return super(RegistrationDocument, self).create(vals_list)
    
    @api.constrains('document_file', 'max_file_size')
    def _check_file_size(self):
        """Validate file size doesn't exceed maximum"""
        for record in self:
            if record.document_file:
                # Convert binary to size in MB
                import base64
                file_size_mb = len(base64.b64decode(record.document_file)) / (1024 * 1024)
                if file_size_mb > record.max_file_size:
                    raise ValidationError(
                        _('File size (%.2f MB) exceeds maximum allowed size (%d MB)') % 
                        (file_size_mb, record.max_file_size)
                    )
    
    def action_upload(self):
        """Mark document as uploaded"""
        for record in self:
            if not record.document_file:
                raise UserError(_('Please upload a document file first.'))
            
            record.write({
                'state': 'uploaded',
                'submitted_by_id': self.env.user.id,
                'submission_date': fields.Datetime.now()
            })
            
            record.message_post(
                body=_('Document uploaded: %s') % record.document_filename,
                message_type='notification'
            )
            
            _logger.info(f'Document {record.name} uploaded for registration {record.registration_id.name}')
        
        return True
    
    def action_start_review(self):
        """Start reviewing the document"""
        for record in self:
            if record.state != 'uploaded':
                raise UserError(_('Only uploaded documents can be reviewed.'))
            
            record.write({
                'state': 'under_review',
                'reviewed_by_id': self.env.user.id,
                'review_date': fields.Datetime.now()
            })
            
            record.message_post(
                body=_('Document review started by %s') % self.env.user.name,
                message_type='notification'
            )
        
        return True
    
    def action_approve(self):
        """Approve the document"""
        for record in self:
            if record.state not in ['uploaded', 'under_review']:
                raise UserError(_('Only uploaded or under-review documents can be approved.'))
            
            record.write({
                'state': 'approved',
                'reviewed_by_id': self.env.user.id,
                'review_date': fields.Datetime.now()
            })
            
            record.message_post(
                body=_('Document approved by %s.<br/>Notes: %s') % (self.env.user.name, record.review_notes or 'N/A'),
                message_type='notification'
            )
            
            # Check if all mandatory documents are approved
            record.registration_id._check_all_documents_approved()
            
            _logger.info(f'Document {record.name} approved')
        
        return True
    
    def action_reject(self):
        """Reject the document - requires reupload"""
        for record in self:
            if record.state not in ['uploaded', 'under_review']:
                raise UserError(_('Only uploaded or under-review documents can be rejected.'))
            
            if not record.rejection_reason:
                raise UserError(_('Please provide a rejection reason.'))
            
            record.write({
                'state': 'rejected',
                'reviewed_by_id': self.env.user.id,
                'review_date': fields.Datetime.now()
            })
            
            record.message_post(
                body=_('Document rejected by %s.<br/>Reason: %s') % (self.env.user.name, record.rejection_reason),
                message_type='notification'
            )
            
            # Notify student via registration chatter
            record.registration_id.message_post(
                body=_('Document "%s" rejected. Please reupload.<br/>Reason: %s') % (record.document_name or record.document_type, record.rejection_reason),
                message_type='notification'
            )
            
            _logger.info(f'Document {record.name} rejected - reupload required')
        
        return True
    
    def action_reset(self):
        """Reset document to pending state"""
        for record in self:
            record.write({
                'state': 'pending',
                'document_file': False,
                'document_filename': False,
                'review_notes': False,
                'rejection_reason': False,
                'reviewed_by_id': False,
                'review_date': False,
                'submitted_by_id': False,
                'submission_date': False
            })
            
            record.message_post(
                body=_('Document reset to pending state'),
                message_type='notification'
            )
        
        return True

