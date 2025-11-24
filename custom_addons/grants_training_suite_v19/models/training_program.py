# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class TrainingProgram(models.Model):
    _name = 'gr.training.program'
    _description = 'Training Program Definition'
    _order = 'name'

    name = fields.Char(
        string='Program Name',
        required=True,
        help='Name of the training program'
    )
    
    description = fields.Text(
        string='Description',
        help='Detailed description of the training program'
    )
    
    short_description = fields.Char(
        string='Short Description',
        size=200,
        help='Brief summary for course cards and listings'
    )
    
    # Enhanced filtering and search fields
    category_id = fields.Many2one(
        'gr.course.category',
        string='Category',
        help='Course category for filtering and organization'
    )
    
    duration_type = fields.Selection([
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months')
    ], string='Duration Type', default='weeks')
    
    duration_value = fields.Float(
        string='Duration Value',
        help='Numeric value for duration'
    )
    
    duration_display = fields.Char(
        string='Duration Display',
        compute='_compute_duration_display',
        store=True,
        help='Human-readable duration'
    )
    
    # Pricing fields
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    price_min = fields.Monetary(
        string='Minimum Price',
        currency_field='currency_id',
        help='Starting price for the course'
    )
    
    price_max = fields.Monetary(
        string='Maximum Price',
        currency_field='currency_id',
        help='Maximum price (for tiered pricing)'
    )
    
    price_display = fields.Char(
        string='Price Display',
        compute='_compute_price_display',
        store=True
    )
    
    # Scheduling
    start_date = fields.Date(
        string='Available From',
        help='Date when course becomes available for enrollment'
    )
    
    end_date = fields.Date(
        string='Available Until',
        help='Last date for enrollment'
    )
    
    # Course details
    difficulty_level = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ], string='Difficulty Level', default='beginner')
    
    language = fields.Selection([
        ('ar', 'Arabic'),
        ('en', 'English'),
        ('ar_en', 'Bilingual (Arabic/English)')
    ], string='Language', default='ar')
    
    instructor_ids = fields.Many2many(
        'res.partner',
        'training_program_instructor_rel',
        'program_id',
        'partner_id',
        string='Instructors',
        domain=[('is_company', '=', False)]
    )
    
    # Rating and reviews
    rating_avg = fields.Float(
        string='Average Rating',
        compute='_compute_rating_avg',
        store=True,
        help='Average rating from student reviews'
    )
    
    review_count = fields.Integer(
        string='Reviews',
        compute='_compute_review_count',
        store=True
    )
    
    review_ids = fields.One2many(
        'gr.course.review',
        'course_id',
        string='Reviews'
    )
    
    # Popularity indicators
    enrollment_count = fields.Integer(
        string='Students Enrolled',
        compute='_compute_enrollment_count',
        store=True
    )
    
    is_featured = fields.Boolean(
        string='Featured Course',
        default=False,
        help='Display this course prominently'
    )
    
    is_popular = fields.Boolean(
        string='Popular Course',
        compute='_compute_is_popular',
        store=True,
        help='Automatically marked based on enrollment numbers'
    )
    
    # Course content details
    learning_objectives = fields.Text(
        string='Learning Objectives',
        help='What students will learn (one per line)'
    )
    
    target_audience = fields.Text(
        string='Target Audience',
        help='Who this course is for (one per line)'
    )
    
    prerequisites = fields.Text(
        string='Prerequisites',
        help='Required knowledge or skills (one per line)'
    )
    
    # Media
    image_url = fields.Char(
        string='Course Image URL',
        help='URL to course thumbnail image'
    )
    
    video_count = fields.Integer(
        string='Video Count',
        default=0,
        help='Number of video lessons'
    )
    
    resource_count = fields.Integer(
        string='Resource Count',
        default=0,
        help='Number of downloadable resources'
    )
    
    # State for public visibility
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], string='State', default='draft')
    
    # Related courses
    related_course_ids = fields.Many2many(
        'gr.training.program',
        'training_program_related_rel',
        'program_id',
        'related_id',
        string='Related Courses'
    )
    
    description = fields.Text(
        string='Description',
        help='Detailed description of the training program'
    )
    
    # Program Structure
    course_integrations = fields.One2many(
        'gr.course.integration',
        'training_program_id',
        string='Course Integrations'
    )
    
    # Requirements
    eligibility_criteria = fields.Text(
        string='Eligibility Criteria',
        help='Specific criteria for this program'
    )
    
    duration_weeks = fields.Integer(
        string='Duration (Weeks)',
        help='Expected program duration in weeks'
    )
    
    # Certification
    # TODO: Create gr.certificate.template model in future phase
    # certificate_template_id = fields.Many2one(
    #     'gr.certificate.template',
    #     string='Certificate Template',
    #     help='Template to use for program completion certificates'
    # )
    
    # Status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived')
    ], string='Status', default='draft')
    
    # Statistics
    total_courses = fields.Integer(
        string='Total Courses',
        compute='_compute_total_courses',
        store=True
    )
    
    enrolled_students = fields.Integer(
        string='Enrolled Students',
        compute='_compute_enrolled_students',
        store=True
    )
    
    completed_students = fields.Integer(
        string='Completed Students',
        compute='_compute_completed_students',
        store=True
    )
    
    # Computed fields
    completion_rate = fields.Float(
        string='Completion Rate (%)',
        compute='_compute_completion_rate',
        store=True
    )
    
    @api.depends('course_integrations')
    def _compute_total_courses(self):
        """Compute total number of courses in the program."""
        for record in self:
            record.total_courses = len(record.course_integrations)
    
    @api.depends('course_integrations', 'course_integrations.enrolled_students')
    def _compute_enrolled_students(self):
        """Compute total enrolled students across all courses."""
        for record in self:
            record.enrolled_students = sum(
                course.enrolled_students for course in record.course_integrations
            )
    
    @api.depends('course_integrations', 'course_integrations.completed_students')
    def _compute_completed_students(self):
        """Compute total completed students across all courses."""
        for record in self:
            record.completed_students = sum(
                course.completed_students for course in record.course_integrations
            )
    
    @api.depends('enrolled_students', 'completed_students')
    def _compute_completion_rate(self):
        """Compute overall completion rate for the program."""
        for record in self:
            if record.enrolled_students > 0:
                record.completion_rate = (record.completed_students / record.enrolled_students) * 100
            else:
                record.completion_rate = 0.0
    
    @api.depends('duration_value', 'duration_type')
    def _compute_duration_display(self):
        """Compute human-readable duration string."""
        for record in self:
            if record.duration_value and record.duration_type:
                value = int(record.duration_value) if record.duration_value.is_integer() else record.duration_value
                unit = dict(record._fields['duration_type'].selection).get(record.duration_type, '')
                record.duration_display = f"{value} {unit}"
            else:
                record.duration_display = ''
    
    @api.depends('price_min', 'price_max', 'currency_id')
    def _compute_price_display(self):
        """Compute formatted price display string."""
        for record in self:
            if record.price_min == 0:
                record.price_display = 'Free'
            elif record.price_min == record.price_max:
                record.price_display = f"{record.currency_id.symbol}{record.price_min:.0f}"
            else:
                record.price_display = f"{record.currency_id.symbol}{record.price_min:.0f} - {record.currency_id.symbol}{record.price_max:.0f}"
    
    @api.depends('review_ids', 'review_ids.rating')
    def _compute_rating_avg(self):
        """Compute average rating from reviews."""
        for record in self:
            if record.review_ids:
                record.rating_avg = sum(review.rating for review in record.review_ids) / len(record.review_ids)
            else:
                record.rating_avg = 0.0
    
    @api.depends('review_ids')
    def _compute_review_count(self):
        """Count number of reviews."""
        for record in self:
            record.review_count = len(record.review_ids)
    
    def _compute_enrollment_count(self):
        """Compute total enrollment count."""
        for record in self:
            # This would be connected to actual enrollment records
            # For now, using the enrolled_students field
            record.enrollment_count = record.enrolled_students
    
    @api.depends('enrollment_count')
    def _compute_is_popular(self):
        """Mark course as popular if it has high enrollment."""
        POPULAR_THRESHOLD = 50  # Can be configured
        for record in self:
            record.is_popular = record.enrollment_count >= POPULAR_THRESHOLD
    
    @api.constrains('duration_weeks')
    def _check_duration_weeks(self):
        """Validate duration weeks."""
        for record in self:
            if record.duration_weeks and record.duration_weeks < 1:
                raise ValidationError(_('Duration must be at least 1 week.'))
    
    def action_activate(self):
        """Activate the training program."""
        for record in self:
            if record.status == 'draft':
                record.status = 'active'
                _logger.info('Training program activated: %s', record.name)
    
    def action_archive(self):
        """Archive the training program."""
        for record in self:
            if record.status == 'active':
                record.status = 'archived'
                _logger.info('Training program archived: %s', record.name)
    
    def action_enroll_eligible_students(self):
        """Open enrollment wizard for eligible students."""
        for record in self:
            if record.status != 'active':
                raise UserError(_('Only active training programs can enroll students.'))
            
            # Create enrollment wizard
            wizard = self.env['gr.enrollment.wizard'].create({
                'training_program_id': record.id,
                'enrollment_type': 'direct_enroll',
                'student_selection_type': 'all_eligible',
                'filter_by_state': 'both',
                'filter_by_english_level': 'any',
                'filter_by_course_preference': True,
                'send_notification': True,
                'auto_assign_agent': True,
            })
            
            return {
                'name': _('Enroll Students in %s') % record.name,
                'type': 'ir.actions.act_window',
                'res_model': 'gr.enrollment.wizard',
                'res_id': wizard.id,
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_training_program_id': record.id,
                }
            }
    
    def action_enroll_with_wizard(self):
        """Open enrollment wizard with advanced options."""
        for record in self:
            if record.status != 'active':
                raise UserError(_('Only active training programs can enroll students.'))
            
            # Create enrollment wizard with advanced options
            wizard = self.env['gr.enrollment.wizard'].create({
                'training_program_id': record.id,
                'enrollment_type': 'direct_enroll',
                'student_selection_type': 'filtered_students',
                'filter_by_state': 'both',
                'filter_by_english_level': 'any',
                'filter_by_course_preference': True,
                'send_notification': True,
                'auto_assign_agent': True,
            })
            
            return {
                'name': _('Advanced Student Enrollment - %s') % record.name,
                'type': 'ir.actions.act_window',
                'res_model': 'gr.enrollment.wizard',
                'res_id': wizard.id,
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_training_program_id': record.id,
                }
            }
    
    def action_generate_certificates(self):
        """Generate certificates for completed students."""
        for record in self:
            # TODO: Add certificate template validation when gr.certificate.template model is created
            # if not record.certificate_template_id:
            #     raise ValidationError(_('No certificate template configured for this program.'))
            
            # Get students who completed all courses
            completed_students = self._get_completed_students()
            
            certificates_created = 0
            for student in completed_students:
                # Check if certificate already exists
                existing_cert = self.env['gr.certificate'].search([
                    ('student_id', '=', student.id),
                    ('certificate_type', '=', 'program_completion'),
                    ('training_program_id', '=', record.id)
                ])
                
                if not existing_cert:
                    self.env['gr.certificate'].create({
                        'student_id': student.id,
                        'certificate_type': 'program_completion',
                        'training_program_id': record.id,
                        'state': 'draft'
                    })
                    certificates_created += 1
            
            _logger.info('Generated %d certificates for program: %s', certificates_created, record.name)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Certificates Generated'),
                    'message': _('Generated %d certificates for program: %s') % (certificates_created, record.name),
                    'type': 'success',
                }
            }
    
    def _get_completed_students(self):
        """Get students who have completed all courses in the program."""
        completed_students = []
        
        for record in self:
            # Get all students enrolled in any course of this program
            all_students = set()
            for course in record.course_integrations:
                for tracker in course.progress_trackers:
                    all_students.add(tracker.student_id.id)
            
            # Check each student's completion status
            for student_id in all_students:
                student = self.env['gr.student'].browse(student_id)
                all_courses_completed = True
                
                for course in record.course_integrations:
                    tracker = self.env['gr.progress.tracker'].search([
                        ('student_id', '=', student_id),
                        ('course_integration_id', '=', course.id)
                    ])
                    
                    if not tracker or tracker.status != 'completed':
                        all_courses_completed = False
                        break
                
                if all_courses_completed:
                    completed_students.append(student)
        
        return completed_students
