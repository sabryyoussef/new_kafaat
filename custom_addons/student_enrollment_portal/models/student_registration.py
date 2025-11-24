# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class StudentRegistration(models.Model):
    _name = 'student.registration'
    _description = 'Student Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Basic Information
    active = fields.Boolean(
        string='Active',
        default=True
    )
    name = fields.Char(
        string='Registration Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    student_name_english = fields.Char(
        string='Student Name (English)',
        required=True,
        tracking=True
    )
    student_name_arabic = fields.Char(
        string='Student Name (Arabic)',
        required=True,
        tracking=True
    )
    
    # Contact Information
    email = fields.Char(
        string='Email',
        required=True,
        tracking=True
    )
    phone = fields.Char(
        string='Phone',
        required=True,
        tracking=True
    )
    
    # Personal Information
    birth_date = fields.Date(
        string='Birth Date',
        required=True,
        tracking=True
    )
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender', required=True, tracking=True)
    
    nationality = fields.Char(
        string='Nationality',
        required=True,
        tracking=True
    )
    
    # Educational Background
    english_level = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], string='English Level', required=True, tracking=True)
    
    native_language = fields.Char(
        string='Native Language',
        default='Arabic',
        tracking=True
    )
    
    has_previous_certificate = fields.Boolean(
        string='Has Previous Certificate',
        tracking=True
    )
    
    certificate_type = fields.Char(
        string='Certificate Type',
        tracking=True
    )
    
    requested_courses = fields.Text(
        string='Requested Courses',
        help='Courses student wants to enroll in',
        tracking=True
    )
    
    # Workflow State
    state = fields.Selection([
        ('draft', 'New Registration'),
        ('submitted', 'Submitted'),
        ('eligibility_review', 'Eligibility Review'),
        ('document_review', 'Document Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('enrolled', 'Enrolled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Review Information
    eligibility_notes = fields.Text(
        string='Eligibility Notes',
        tracking=True
    )
    
    document_notes = fields.Text(
        string='Document Notes',
        tracking=True
    )
    
    rejection_reason = fields.Text(
        string='Rejection Reason',
        tracking=True
    )
    
    reviewer_id = fields.Many2one(
        'res.users',
        string='Reviewer',
        tracking=True
    )
    
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        tracking=True
    )
    
    approved_date = fields.Datetime(
        string='Approval Date',
        tracking=True
    )
    
    # Related Records
    student_id = fields.Many2one(
        'gr.student',
        string='Student Record',
        readonly=True,
        tracking=True
    )
    
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'student_registration_attachment_rel',
        'registration_id',
        'attachment_id',
        string='Documents'
    )
    
    attachment_count = fields.Integer(
        string='Document Count',
        compute='_compute_attachment_count'
    )
    
    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = len(record.attachment_ids)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('student.registration') or _('New')
        return super(StudentRegistration, self).create(vals)
    
    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                # Basic email validation
                if '@' not in record.email or '.' not in record.email:
                    raise ValidationError(_('Please enter a valid email address.'))
    
    def action_submit(self):
        """Student submits registration"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Only draft registrations can be submitted.'))
            
            record.write({'state': 'submitted'})
            
            # Send notification to admins
            self._send_notification_to_admins()
            
            # Log message
            record.message_post(
                body=_('Registration submitted by student.'),
                message_type='notification'
            )
            
            _logger.info(f'Registration {record.name} submitted by student')
        
        return True
    
    def action_start_eligibility_review(self):
        """Admin starts eligibility review"""
        for record in self:
            if record.state != 'submitted':
                raise UserError(_('Only submitted registrations can be reviewed.'))
            
            record.write({
                'state': 'eligibility_review',
                'reviewer_id': self.env.user.id
            })
            
            record.message_post(
                body=_('Eligibility review started by %s.') % self.env.user.name,
                message_type='notification'
            )
            
            _logger.info(f'Eligibility review started for {record.name} by {self.env.user.name}')
        
        return True
    
    def action_approve_eligibility(self):
        """Approve eligibility, move to document review"""
        for record in self:
            if record.state != 'eligibility_review':
                raise UserError(_('Only registrations in eligibility review can be approved.'))
            
            if not record.eligibility_notes:
                raise UserError(_('Please add eligibility notes before approving.'))
            
            record.write({'state': 'document_review'})
            
            record.message_post(
                body=_('Eligibility approved. Moving to document review.<br/>Notes: %s') % record.eligibility_notes,
                message_type='notification'
            )
            
            _logger.info(f'Eligibility approved for {record.name}')
        
        return True
    
    def action_reject_eligibility(self):
        """Reject at eligibility stage"""
        for record in self:
            if record.state != 'eligibility_review':
                raise UserError(_('Only registrations in eligibility review can be rejected.'))
            
            if not record.rejection_reason:
                raise UserError(_('Please provide a rejection reason.'))
            
            record.write({'state': 'rejected'})
            
            # Send rejection email to student
            self._send_rejection_email()
            
            record.message_post(
                body=_('Registration rejected at eligibility stage.<br/>Reason: %s') % record.rejection_reason,
                message_type='notification'
            )
            
            _logger.info(f'Registration {record.name} rejected at eligibility stage')
        
        return True
    
    def action_approve_documents(self):
        """Approve documents, move to approved"""
        for record in self:
            if record.state != 'document_review':
                raise UserError(_('Only registrations in document review can be approved.'))
            
            if not record.document_notes:
                raise UserError(_('Please add document review notes before approving.'))
            
            record.write({'state': 'approved'})
            
            record.message_post(
                body=_('Documents approved.<br/>Notes: %s') % record.document_notes,
                message_type='notification'
            )
            
            _logger.info(f'Documents approved for {record.name}')
        
        return True
    
    def action_reject_documents(self):
        """Reject at document stage"""
        for record in self:
            if record.state != 'document_review':
                raise UserError(_('Only registrations in document review can be rejected.'))
            
            if not record.rejection_reason:
                raise UserError(_('Please provide a rejection reason.'))
            
            record.write({'state': 'rejected'})
            
            # Send rejection email to student
            self._send_rejection_email()
            
            record.message_post(
                body=_('Registration rejected at document review stage.<br/>Reason: %s') % record.rejection_reason,
                message_type='notification'
            )
            
            _logger.info(f'Registration {record.name} rejected at document stage')
        
        return True
    
    def action_final_approve(self):
        """Final approval - create student record and portal user"""
        for record in self:
            if record.state != 'approved':
                raise UserError(_('Only approved registrations can be finalized.'))
            
            # Create student record
            student = record._create_student_record()
            
            # Create portal user
            portal_user = record._create_portal_user()
            
            record.write({
                'student_id': student.id,
                'approved_by': self.env.user.id,
                'approved_date': fields.Datetime.now()
            })
            
            # Send approval email with login credentials
            self._send_approval_email(portal_user)
            
            record.message_post(
                body=_('Registration finalized. Student record created: %s. Portal user created: %s') % (student.name, portal_user.login),
                message_type='notification'
            )
            
            _logger.info(f'Registration {record.name} finalized - Student: {student.id}, User: {portal_user.id}')
        
        return True
    
    def action_enroll_student(self):
        """Open wizard to enroll student in courses"""
        for record in self:
            if not record.student_id:
                raise UserError(_('Please finalize the registration first to create a student record.'))
            
            # Return action to open enrollment wizard
            return {
                'name': _('Enroll Student in Courses'),
                'type': 'ir.actions.act_window',
                'res_model': 'gr.course.session',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_student_id': record.student_id.id,
                    'default_registration_id': record.id,
                }
            }
    
    def _create_student_record(self):
        """Create gr.student record from registration"""
        self.ensure_one()
        
        student_vals = {
            'name': self.student_name_english,
            'name_arabic': self.student_name_arabic,
            'email': self.email,
            'phone': self.phone,
            'birth_date': self.birth_date,
            'gender': self.gender,
            'nationality': self.nationality,
            'english_level': self.english_level,
            'native_language': self.native_language,
        }
        
        student = self.env['gr.student'].create(student_vals)
        
        _logger.info(f'Created student record {student.id} from registration {self.name}')
        
        return student
    
    def _create_portal_user(self):
        """Create portal user for student"""
        self.ensure_one()
        
        # Check if user already exists
        existing_user = self.env['res.users'].search([('login', '=', self.email)], limit=1)
        if existing_user:
            _logger.warning(f'User with email {self.email} already exists')
            return existing_user
        
        # Get portal group
        portal_group = self.env.ref('base.group_portal')
        
        # Create partner
        partner_vals = {
            'name': self.student_name_english,
            'email': self.email,
            'phone': self.phone,
        }
        partner = self.env['res.partner'].create(partner_vals)
        
        # Create user
        user_vals = {
            'name': self.student_name_english,
            'login': self.email,
            'partner_id': partner.id,
            'groups_id': [(6, 0, [portal_group.id])],
        }
        
        user = self.env['res.users'].create(user_vals)
        
        # Send password reset email
        user.action_reset_password()
        
        _logger.info(f'Created portal user {user.id} for registration {self.name}')
        
        return user
    
    def _send_notification_to_admins(self):
        """Send notification to admins when registration is submitted"""
        self.ensure_one()
        
        # Get manager and agent groups
        manager_group = self.env.ref('grants_training_suite_v19.group_manager')
        agent_group = self.env.ref('grants_training_suite_v19.group_agent')
        
        # Get all users in these groups
        admin_users = manager_group.users | agent_group.users
        
        # Send notification
        if admin_users:
            self.message_subscribe(partner_ids=admin_users.mapped('partner_id').ids)
            self.message_post(
                body=_('New student registration submitted: %s') % self.name,
                message_type='notification',
                partner_ids=admin_users.mapped('partner_id').ids
            )
    
    def _send_rejection_email(self):
        """Send rejection email to student"""
        self.ensure_one()
        
        template = self.env.ref('student_enrollment_portal.email_template_registration_rejected', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
    
    def _send_approval_email(self, portal_user):
        """Send approval email with login credentials"""
        self.ensure_one()
        
        template = self.env.ref('student_enrollment_portal.email_template_registration_approved', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

