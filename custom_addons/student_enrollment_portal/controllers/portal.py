# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
import base64
import logging

_logger = logging.getLogger(__name__)


class StudentPortal(CustomerPortal):
    
    @http.route(['/student/register'], type='http', auth='public', website=True, sitemap=False)
    def student_registration_form(self, **kw):
        """Display the student registration form"""
        
        # Get available courses
        courses = request.env['gr.course.integration'].sudo().search([])
        
        values = {
            'courses': courses,
            'post': kw,  # Pass form data for repopulation
            'error': {},
            'error_message': []
        }
        
        return request.render('student_enrollment_portal.portal_student_registration_form', values)
    
    @http.route(['/student/register/submit'], type='http', auth='public', website=True, methods=['POST'], csrf=False)
    def student_registration_submit(self, **post):
        """Handle student registration form submission"""
        
        error = {}
        error_message = []
        
        # Validate required fields
        required_fields = [
            'student_name_english', 'student_name_arabic', 'email', 'phone',
            'birth_date', 'gender', 'nationality', 'english_level'
        ]
        
        for field in required_fields:
            if not post.get(field):
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
        
        # Prepare registration data
        registration_vals = {
            'student_name_english': post.get('student_name_english'),
            'student_name_arabic': post.get('student_name_arabic'),
            'email': post.get('email'),
            'phone': post.get('phone'),
            'birth_date': post.get('birth_date'),
            'gender': post.get('gender'),
            'nationality': post.get('nationality'),
            'english_level': post.get('english_level'),
            'native_language': post.get('native_language', 'Arabic'),
            'has_previous_certificate': bool(post.get('has_previous_certificate')),
            'certificate_type': post.get('certificate_type') if post.get('has_previous_certificate') else False,
            'requested_courses': post.get('requested_courses', ''),
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
            _logger.error(f'Error creating student registration: {str(e)}')
            error_message.append(_('An error occurred while submitting your registration. Please try again.'))
            
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
    
    def _prepare_home_portal_values(self, counters):
        """Add registration count to portal home"""
        values = super()._prepare_home_portal_values(counters)
        
        user = request.env.user
        
        if 'registration_count' in counters:
            registration_count = request.env['student.registration'].search_count([
                ('email', '=', user.email)
            ]) if user.email else 0
            values['registration_count'] = registration_count
        
        return values

