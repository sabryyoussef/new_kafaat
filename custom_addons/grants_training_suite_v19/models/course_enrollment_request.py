# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class CourseEnrollmentRequest(models.Model):
    _name = 'course.enrollment.request'
    _description = 'Course Enrollment Request'
    _order = 'request_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Request Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        help='Unique request number'
    )

    student_id = fields.Many2one(
        'gr.student',
        string='Student',
        required=True,
        tracking=True,
        help='Student requesting enrollment'
    )

    student_email = fields.Char(
        string='Student Email',
        related='student_id.email',
        store=True,
        help='Email of the student'
    )

    course_integration_id = fields.Many2one(
        'gr.course.integration',
        string='Course',
        required=True,
        tracking=True,
        help='Course to enroll in'
    )

    course_name = fields.Char(
        string='Course Name',
        related='course_integration_id.name',
        store=True,
        help='Name of the course'
    )

    request_date = fields.Datetime(
        string='Request Date',
        default=fields.Datetime.now,
        required=True,
        tracking=True,
        help='Date when the request was submitted'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', required=True, tracking=True)

    notes = fields.Text(
        string='Student Notes',
        help='Notes from the student about why they want to enroll'
    )

    admin_notes = fields.Text(
        string='Admin Notes',
        tracking=True,
        help='Internal notes from admin/agent'
    )

    rejection_reason = fields.Text(
        string='Rejection Reason',
        tracking=True,
        help='Reason for rejection (shown to student)'
    )

    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        tracking=True,
        help='User who approved the request'
    )

    approved_date = fields.Datetime(
        string='Approval Date',
        readonly=True,
        tracking=True,
        help='Date when the request was approved'
    )

    rejected_by = fields.Many2one(
        'res.users',
        string='Rejected By',
        readonly=True,
        tracking=True,
        help='User who rejected the request'
    )

    rejected_date = fields.Datetime(
        string='Rejection Date',
        readonly=True,
        tracking=True,
        help='Date when the request was rejected'
    )

    session_id = fields.Many2one(
        'gr.course.session',
        string='Created Session',
        readonly=True,
        help='Course session created upon approval'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate sequence number"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('course.enrollment.request') or _('New')
        return super(CourseEnrollmentRequest, self).create(vals_list)

    def action_submit(self):
        """Submit request for approval"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Only draft requests can be submitted.'))
            
            # Check if student already has a pending or approved request for this course
            existing_request = self.search([
                ('student_id', '=', record.student_id.id),
                ('course_integration_id', '=', record.course_integration_id.id),
                ('state', 'in', ['pending', 'approved']),
                ('id', '!=', record.id)
            ], limit=1)
            
            if existing_request:
                raise ValidationError(_(
                    'You already have a %s request for this course. '
                    'Please wait for it to be processed.'
                ) % existing_request.state)
            
            # Check if student is already enrolled in this course
            existing_session = self.env['gr.course.session'].search([
                ('student_id', '=', record.student_id.id),
                ('course_integration_id', '=', record.course_integration_id.id),
            ], limit=1)
            
            if existing_session:
                raise ValidationError(_('You are already enrolled in this course.'))
            
            record.state = 'pending'
            record.request_date = fields.Datetime.now()
            
            # Send notification to admins
            record._send_notification_to_admins()
            
            _logger.info(f'Enrollment request {record.name} submitted by student {record.student_id.name}')

    def action_approve(self):
        """Approve enrollment request and create course session"""
        for record in self:
            if record.state != 'pending':
                raise UserError(_('Only pending requests can be approved.'))
            
            record.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approved_date': fields.Datetime.now(),
            })
            
            # Create course session
            session = record._create_course_session()
            record.session_id = session.id
            
            # Send approval email
            record._send_approval_email()
            
            _logger.info(f'Enrollment request {record.name} approved, session {session.name} created')

    def action_reject(self):
        """Reject enrollment request"""
        for record in self:
            if record.state != 'pending':
                raise UserError(_('Only pending requests can be rejected.'))
            
            if not record.rejection_reason:
                raise ValidationError(_('Please provide a rejection reason.'))
            
            record.write({
                'state': 'rejected',
                'rejected_by': self.env.user.id,
                'rejected_date': fields.Datetime.now(),
            })
            
            # Send rejection email
            record._send_rejection_email()
            
            _logger.info(f'Enrollment request {record.name} rejected')

    def action_reset_to_draft(self):
        """Reset request to draft"""
        for record in self:
            if record.state not in ['rejected']:
                raise UserError(_('Only rejected requests can be reset to draft.'))
            
            record.write({
                'state': 'draft',
                'rejection_reason': False,
                'rejected_by': False,
                'rejected_date': False,
            })

    def _create_course_session(self):
        """Create course session for approved request"""
        self.ensure_one()
        
        # Calculate next Monday as default session date
        today = datetime.now()
        days_ahead = 0 - today.weekday()  # Monday is 0
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        next_monday = next_monday.replace(hour=9, minute=0, second=0, microsecond=0)
        
        session_vals = {
            'name': f'{self.course_integration_id.name} - {self.student_id.name}',
            'student_id': self.student_id.id,
            'course_integration_id': self.course_integration_id.id,
            'session_date': next_monday,
            'session_duration': 1.0,  # Default 1 hour
            'state': 'scheduled',
            'notes': f'Created from enrollment request {self.name}',
        }
        
        session = self.env['gr.course.session'].sudo().create(session_vals)
        
        return session

    def _send_notification_to_admins(self):
        """Send email notification to admins about new request"""
        self.ensure_one()
        
        template = self.env.ref(
            'grants_training_suite_v19.email_template_enrollment_request_submitted',
            raise_if_not_found=False
        )
        
        if template:
            # Get manager and agent groups
            manager_group = self.env.ref('grants_training_suite_v19.group_manager', raise_if_not_found=False)
            agent_group = self.env.ref('grants_training_suite_v19.group_agent', raise_if_not_found=False)
            
            if manager_group and agent_group:
                admin_users = self.env['res.users'].search([
                    '|',
                    ('groups_id', '=', manager_group.id),
                    ('groups_id', '=', agent_group.id)
                ])
                
                for user in admin_users:
                    if user.email:
                        template.sudo().send_mail(
                            self.id,
                            force_send=True,
                            email_values={'email_to': user.email}
                        )

    def _send_approval_email(self):
        """Send approval email to student"""
        self.ensure_one()
        
        template = self.env.ref(
            'grants_training_suite_v19.email_template_enrollment_request_approved',
            raise_if_not_found=False
        )
        
        if template:
            template.sudo().send_mail(self.id, force_send=True)

    def _send_rejection_email(self):
        """Send rejection email to student"""
        self.ensure_one()
        
        template = self.env.ref(
            'grants_training_suite_v19.email_template_enrollment_request_rejected',
            raise_if_not_found=False
        )
        
        if template:
            template.sudo().send_mail(self.id, force_send=True)

