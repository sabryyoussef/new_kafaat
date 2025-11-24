# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class DocumentRequestPortal(models.Model):
    _name = 'gr.document.request.portal'
    _description = 'Student Document Request'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Request Number',
        required=True,
        default=lambda self: _('New'),
        copy=False,
        readonly=True,
        tracking=True,
        help='Unique request number'
    )
    
    student_id = fields.Many2one(
        'gr.student',
        string='Student',
        required=True,
        tracking=True,
        help='Student making the request'
    )
    
    request_type = fields.Selection([
        ('upload', 'Upload Document'),
        ('download', 'Request Academy Document')
    ], string='Request Type', required=True, tracking=True,
       help='Type of document request')
    
    document_type = fields.Selection([
        ('id', 'ID/Passport'),
        ('transcript', 'Transcript'),
        ('certificate', 'Certificate'),
        ('attendance', 'Attendance Record'),
        ('other', 'Other')
    ], string='Document Type', required=True, tracking=True,
       help='Type of document being requested or uploaded')
    
    description = fields.Text(
        string='Description',
        help='Additional details about the request'
    )
    
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', required=True, tracking=True,
       help='Current status of the request')
    
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'document_request_attachment_rel',
        'request_id',
        'attachment_id',
        string='Attachments',
        help='Files attached to this request'
    )
    
    response_note = fields.Text(
        string='Admin Response',
        tracking=True,
        help='Response from academy administration'
    )
    
    create_date = fields.Datetime(
        string='Request Date',
        readonly=True
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Generate sequence number for new requests"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('gr.document.request.portal') or _('New')
        return super(DocumentRequestPortal, self).create(vals_list)
    
    def action_submit(self):
        """Submit the request"""
        for record in self:
            if record.status == 'draft':
                record.status = 'submitted'
                record.message_post(body=_('Document request submitted'))
    
    def action_set_in_progress(self):
        """Mark request as in progress"""
        for record in self:
            if record.status == 'submitted':
                record.status = 'in_progress'
                record.message_post(body=_('Document request is being processed'))
    
    def action_complete(self):
        """Mark request as completed"""
        for record in self:
            if record.status in ['submitted', 'in_progress']:
                record.status = 'completed'
                record.message_post(body=_('Document request completed'))
    
    def action_reject(self):
        """Reject the request"""
        for record in self:
            if record.status in ['submitted', 'in_progress']:
                record.status = 'rejected'
                record.message_post(body=_('Document request rejected'))

