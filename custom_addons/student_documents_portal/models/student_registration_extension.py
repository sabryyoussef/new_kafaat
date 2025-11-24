# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StudentRegistrationExtension(models.Model):
    """
    Extends student.registration to integrate with document management system.
    Replaces attachment_ids with structured document requests.
    """
    _inherit = 'student.registration'
    
    # Deprecate old attachment fields (replaced by structured document requests)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'student_registration_attachment_rel',
        'registration_id',
        'attachment_id',
        string='Documents (Deprecated)',
        help='This field is deprecated. Use Registration Documents instead.'
    )
    
    attachment_count = fields.Integer(
        string='Attachment Count (Deprecated)',
        compute='_compute_attachment_count',
        help='This field is deprecated. Use registration_document_count instead.'
    )
    
    # Replace simple attachments with structured document requests
    registration_document_ids = fields.One2many(
        'gr.registration.document',
        'registration_id',
        string='Registration Documents'
    )
    
    registration_document_count = fields.Integer(
        string='Document Count',
        compute='_compute_registration_document_count'
    )
    
    mandatory_documents_uploaded = fields.Boolean(
        string='All Mandatory Documents Uploaded',
        compute='_compute_mandatory_documents_uploaded',
        store=True,
        help='Whether all mandatory documents have been uploaded'
    )
    
    documents_approved = fields.Boolean(
        string='All Documents Approved',
        compute='_compute_documents_approved',
        store=True,
        help='Whether all mandatory documents have been approved'
    )
    
    @api.depends('registration_document_ids')
    def _compute_registration_document_count(self):
        for record in self:
            record.registration_document_count = len(record.registration_document_ids)
    
    @api.depends('registration_document_ids.state', 'registration_document_ids.is_mandatory')
    def _compute_mandatory_documents_uploaded(self):
        for record in self:
            mandatory_docs = record.registration_document_ids.filtered(lambda d: d.is_mandatory)
            if not mandatory_docs:
                record.mandatory_documents_uploaded = True
            else:
                # All mandatory docs must be at least uploaded (not pending)
                record.mandatory_documents_uploaded = all(
                    doc.state != 'pending' for doc in mandatory_docs
                )
    
    @api.depends('registration_document_ids.state', 'registration_document_ids.is_mandatory')
    def _compute_documents_approved(self):
        for record in self:
            mandatory_docs = record.registration_document_ids.filtered(lambda d: d.is_mandatory)
            if not mandatory_docs:
                record.documents_approved = True
            else:
                # All mandatory docs must be approved
                record.documents_approved = all(
                    doc.state == 'approved' for doc in mandatory_docs
                )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Create default document requests when registration is created"""
        registrations = super(StudentRegistrationExtension, self).create(vals_list)
        
        for registration in registrations:
            registration._create_default_document_requests()
        
        return registrations
    
    def _create_default_document_requests(self):
        """Create standard document requests for new registrations"""
        self.ensure_one()
        
        # Define default documents required for registration
        default_documents = [
            {
                'document_type': 'national_id',
                'document_name': 'National ID / Iqama',
                'document_description': 'Please upload a clear copy of your National ID or Iqama',
                'is_mandatory': True,
                'required_format': 'PDF, JPG, PNG',
                'max_file_size': 5,
            },
            {
                'document_type': 'photo',
                'document_name': 'Personal Photo',
                'document_description': 'Recent passport-size photo with white background',
                'is_mandatory': True,
                'required_format': 'JPG, PNG',
                'max_file_size': 2,
            },
            {
                'document_type': 'educational_certificate',
                'document_name': 'Educational Certificate',
                'document_description': 'Your highest educational certificate or diploma',
                'is_mandatory': True,
                'required_format': 'PDF, JPG, PNG',
                'max_file_size': 5,
            },
        ]
        
        # Add previous training certificate if student has one
        if self.has_previous_certificate:
            default_documents.append({
                'document_type': 'previous_training_certificate',
                'document_name': 'Previous Training Certificate',
                'document_description': f'Certificate: {self.certificate_type or "N/A"}',
                'is_mandatory': False,
                'required_format': 'PDF, JPG, PNG',
                'max_file_size': 5,
            })
        
        # Create document requests
        for doc_data in default_documents:
            doc_data['registration_id'] = self.id
            self.env['gr.registration.document'].create(doc_data)
        
        _logger.info(f'Created {len(default_documents)} default document requests for registration {self.name}')
    
    def _check_all_documents_approved(self):
        """Check if all mandatory documents are approved, called from document approval"""
        self.ensure_one()
        
        if self.documents_approved and self.state == 'document_review':
            # Auto-move to approved state when all documents are approved
            self.message_post(
                body=_('All mandatory documents have been approved automatically.'),
                message_type='notification'
            )
            _logger.info(f'All documents approved for registration {self.name}')
    
    def action_view_documents(self):
        """Open the registration documents view"""
        self.ensure_one()
        
        return {
            'name': _('Registration Documents'),
            'type': 'ir.actions.act_window',
            'res_model': 'gr.registration.document',
            'view_mode': 'list,form',
            'domain': [('registration_id', '=', self.id)],
            'context': {
                'default_registration_id': self.id,
                'search_default_registration_id': self.id,
            },
        }
    
    def action_approve_documents(self):
        """Override to check document approval status"""
        for record in self:
            if not record.documents_approved:
                # Show which documents are not approved
                unapproved = record.registration_document_ids.filtered(
                    lambda d: d.is_mandatory and d.state != 'approved'
                )
                doc_names = ', '.join(unapproved.mapped('document_name'))
                raise UserError(
                    _('Cannot approve documents. The following mandatory documents are not yet approved:\n%s') % doc_names
                )
        
        return super(StudentRegistrationExtension, self).action_approve_documents()
    
    def action_request_additional_document(self):
        """Open wizard to request additional documents from student"""
        self.ensure_one()
        
        return {
            'name': _('Request Additional Document'),
            'type': 'ir.actions.act_window',
            'res_model': 'gr.registration.document',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_registration_id': self.id,
                'default_is_mandatory': False,
            },
        }

