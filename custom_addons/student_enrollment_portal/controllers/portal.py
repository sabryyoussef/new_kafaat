# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
import base64
import logging

_logger = logging.getLogger(__name__)


class StudentEnrollmentPortal(CustomerPortal):
    """Portal controller for student enrollment/registration"""
    
    @http.route(['/student/register'], type='http', auth='public', website=True, sitemap=False)
    def student_registration_form(self, course_id=None, **kw):
        """Display the student registration form"""
        
        # Get available courses
        courses = request.env['gr.course.integration'].sudo().search([])
        
        # Get pre-selected course if course_id is provided
        selected_course = None
        if course_id:
            try:
                selected_course = request.env['gr.course.integration'].sudo().browse(int(course_id))
                if not selected_course.exists():
                    selected_course = None
            except (ValueError, TypeError):
                selected_course = None
        
        values = {
            'courses': courses,
            'selected_course': selected_course,
            'post': kw,  # Pass form data for repopulation
            'error': {},
            'error_message': []
        }
        
        return request.render('student_enrollment_portal.portal_student_registration_form', values)
    
    @http.route(['/student/register/submit'], type='http', auth='public', website=True, methods=['POST'], csrf=False)
    def student_registration_submit(self, **post):
        """Handle student registration form submission"""
        
        # Log the post data for debugging
        _logger.info(f'Registration form submitted with data: {post}')
        
        error = {}
        error_message = []
        
        # Validate required fields
        required_fields = [
            'student_name_english', 'student_name_arabic', 'email', 'phone',
            'birth_date', 'gender', 'nationality', 'english_level'
        ]
        
        for field in required_fields:
            field_value = post.get(field)
            # Handle list values (in case of multiple selections)
            if isinstance(field_value, list):
                field_value = field_value[0] if field_value else None
            if not field_value:
                error[field] = 'missing'
        
        if error:
            error_message.append(_('Please fill in all required fields.'))
        
        # Validate email format
        if post.get('email') and '@' not in post.get('email'):
            error['email'] = 'invalid'
            error_message.append(_('Please enter a valid email address.'))
        
        # If there are errors, re-render the form
        if error_message:
            courses = request.env['gr.course.integration'].sudo().search([])
            values = {
                'courses': courses,
                'error': error,
                'error_message': error_message,
                'post': post
            }
            return request.render('student_enrollment_portal.portal_student_registration_form', values)
        
        # Helper function to get value from post (handles lists)
        def get_post_value(key, default=''):
            value = post.get(key, default)
            # If value is a list, get the first element
            if isinstance(value, list):
                return value[0] if value else default
            return value
        
        # Prepare registration data
        registration_vals = {
            'student_name_english': get_post_value('student_name_english'),
            'student_name_arabic': get_post_value('student_name_arabic'),
            'email': get_post_value('email'),
            'phone': get_post_value('phone'),
            'birth_date': get_post_value('birth_date'),
            'gender': get_post_value('gender'),
            'nationality': get_post_value('nationality'),
            'english_level': get_post_value('english_level'),
            'native_language': get_post_value('native_language', 'Arabic'),
            'has_previous_certificate': bool(get_post_value('has_previous_certificate')),
            'certificate_type': get_post_value('certificate_type') if get_post_value('has_previous_certificate') else False,
            'requested_courses': get_post_value('requested_courses', ''),
            'state': 'draft'
        }
        
        # Create registration record
        try:
            registration = request.env['student.registration'].sudo().create(registration_vals)
            
            # Handle file uploads
            if 'documents' in request.httprequest.files:
                attachments = request.httprequest.files.getlist('documents')
                for attachment in attachments:
                    if attachment and attachment.filename:
                        attached_file = attachment.read()
                        request.env['ir.attachment'].sudo().create({
                            'name': attachment.filename,
                            'datas': base64.b64encode(attached_file),
                            'res_model': 'student.registration',
                            'res_id': registration.id,
                        })
            
            # Submit the registration
            registration.action_submit()
            
            _logger.info(f'New student registration created: {registration.name}')
            
            # Redirect to success page
            return request.redirect('/student/register/success?reg=%s' % registration.name)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            _logger.error(f'Error creating student registration: {str(e)}\n{error_details}')
            
            # Show detailed error in development/debug mode
            error_message.append(_('An error occurred while submitting your registration. Please try again.'))
            error_message.append(_('Error details: %s') % str(e))
            
            courses = request.env['gr.course.integration'].sudo().search([])
            values = {
                'courses': courses,
                'error': error,
                'error_message': error_message,
                'post': post
            }
            return request.render('student_enrollment_portal.portal_student_registration_form', values)
    
    @http.route(['/student/register/success'], type='http', auth='public', website=True, sitemap=False)
    def student_registration_success(self, **kw):
        """Display registration success page"""
        
        reg_number = kw.get('reg')
        
        values = {
            'registration_number': reg_number
        }
        
        return request.render('student_enrollment_portal.portal_registration_success', values)
    
    @http.route(['/my/registration', '/my/registration/<int:reg_id>'], type='http', auth='user', website=True)
    def portal_my_registration(self, reg_id=None, **kw):
        """Display student's registration status"""
        
        user = request.env.user
        
        # Find registration by user email
        if not reg_id:
            registration = request.env['student.registration'].search([
                ('email', '=', user.email)
            ], limit=1, order='create_date desc')
        else:
            try:
                registration = request.env['student.registration'].browse(reg_id)
                # Check access
                if registration.email != user.email:
                    raise AccessError(_('You do not have access to this registration.'))
            except (AccessError, MissingError):
                return request.redirect('/my')
        
        if not registration:
            return request.redirect('/student/register')
        
        values = {
            'registration': registration,
            'page_name': 'registration',
        }
        
        return request.render('student_enrollment_portal.portal_my_registration', values)
    
    @http.route(['/my/registration/<int:reg_id>/upload'], type='http', auth='user', website=True, methods=['POST'], csrf=False)
    def portal_registration_upload(self, reg_id, **post):
        """Upload additional documents to registration"""
        
        user = request.env.user
        
        try:
            registration = request.env['student.registration'].browse(reg_id)
            
            # Check access
            if registration.email != user.email:
                raise AccessError(_('You do not have access to this registration.'))
            
            # Handle file uploads
            if post.get('documents'):
                attachments = request.httprequest.files.getlist('documents')
                for attachment in attachments:
                    if attachment:
                        attached_file = attachment.read()
                        request.env['ir.attachment'].sudo().create({
                            'name': attachment.filename,
                            'datas': base64.b64encode(attached_file),
                            'res_model': 'student.registration',
                            'res_id': registration.id,
                        })
                
                # Add message to chatter
                registration.sudo().message_post(
                    body=_('Student uploaded %s new document(s).') % len(attachments),
                    message_type='notification'
                )
                
                _logger.info(f'Student uploaded documents to registration {registration.name}')
            
        except (AccessError, MissingError) as e:
            _logger.error(f'Error uploading documents: {str(e)}')
        
        return request.redirect('/my/registration/%s' % reg_id)
    
    # NOTE: _prepare_home_portal_values moved to grants_training_suite_v19
    # to avoid method override conflicts. Registration counter is now
    # handled in the main student portal controller.

