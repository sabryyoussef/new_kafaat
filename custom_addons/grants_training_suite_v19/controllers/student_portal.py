# -*- coding: utf-8 -*-

import base64
import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

_logger = logging.getLogger(__name__)


class GrantsStudentPortal(CustomerPortal):
    """Student Portal Controller for Grants Training Suite"""
    
    def _prepare_home_portal_values(self, counters):
        """Add student-related counters to portal home"""
        values = super()._prepare_home_portal_values(counters)
        
        user = request.env.user
        
        # Add course count for enrolled students
        if 'course_count' in counters:
            student = self._get_student_for_portal_user()
            if student:
                values['course_count'] = len(student.course_session_ids)
        
        # Add registration count (from student_enrollment_portal)
        if 'registration_count' in counters:
            registration_count = request.env['student.registration'].search_count([
                ('email', '=', user.email)
            ]) if user.email else 0
            values['registration_count'] = registration_count
        
        return values
    
    def _get_student_for_portal_user(self):
        """Get student record for current portal user"""
        if not request.env.user or request.env.user._is_public():
            return False
        
        # Find student by email matching portal user email
        student = request.env['gr.student'].sudo().search([
            ('email', '=', request.env.user.email)
        ], limit=1)
        
        return student
    
    @http.route(['/my/student'], type='http', auth='user', website=True)
    def portal_my_student_dashboard(self, **kw):
        """Student dashboard - shows student info and enrolled courses"""
        student = self._get_student_for_portal_user()
        
        if not student:
            return request.render('grants_training_suite_v19.portal_no_student')
        
        # Get enrollment requests
        enrollment_requests = request.env['course.enrollment.request'].search([
            ('student_id', '=', student.id)
        ], order='request_date desc', limit=5)
        
        pending_requests = enrollment_requests.filtered(lambda r: r.state == 'pending')
        
        # Get available courses (top 5)
        all_courses = request.env['gr.course.integration'].sudo().search([
            ('status', '=', 'active')
        ], limit=5)
        enrolled_course_ids = student.course_session_ids.mapped('course_integration_id').ids
        available_courses = all_courses.filtered(lambda c: c.id not in enrolled_course_ids)[:3]
        
        values = {
            'page_name': 'student_dashboard',
            'student': student,
            'courses': student.course_session_ids,
            'progress': student.progress_percentage,
            'certificates': student.certificate_ids,
            'enrollment_requests': enrollment_requests,
            'pending_requests': pending_requests,
            'available_courses': available_courses,
        }
        
        return request.render('grants_training_suite_v19.portal_student_dashboard', values)
    
    @http.route(['/my/courses'], type='http', auth='user', website=True)
    def portal_my_courses(self, **kw):
        """List of enrolled courses for student"""
        student = self._get_student_for_portal_user()
        
        if not student:
            return request.render('grants_training_suite_v19.portal_no_student')
        
        values = {
            'page_name': 'my_courses',
            'student': student,
            'sessions': student.course_session_ids,
        }
        
        return request.render('grants_training_suite_v19.portal_my_courses', values)
    
    @http.route(['/my/courses/<int:session_id>'], type='http', auth='user', website=True)
    def portal_course_detail(self, session_id, **kw):
        """Course session detail page"""
        student = self._get_student_for_portal_user()
        
        if not student:
            return request.render('grants_training_suite_v19.portal_no_student')
        
        session = request.env['gr.course.session'].sudo().browse(session_id)
        
        # Verify this session belongs to the student
        if session.student_id != student:
            return request.render('website.403')
        
        values = {
            'page_name': 'course_detail',
            'student': student,
            'session': session,
        }
        
        return request.render('grants_training_suite_v19.portal_course_detail', values)
    
    @http.route(['/my/certificates'], type='http', auth='user', website=True)
    def portal_my_certificates(self, **kw):
        """List of certificates for student"""
        student = self._get_student_for_portal_user()
        
        if not student:
            return request.render('grants_training_suite_v19.portal_no_student')
        
        values = {
            'page_name': 'my_certificates',
            'student': student,
            'certificates': student.certificate_ids,
        }
        
        return request.render('grants_training_suite_v19.portal_my_certificates', values)
    
    @http.route(['/my/enrollments'], type='http', auth='user', website=True)
    def portal_my_enrollments(self, **kw):
        """Enhanced enrollment tracking with basic info"""
        student = self._get_student_for_portal_user()
        if not student:
            return request.render('grants_training_suite_v19.portal_no_student')
        
        # Get all course sessions with status
        sessions = student.course_session_ids
        
        # Calculate completion percentage per session
        enrollment_data = []
        for session in sessions:
            enrollment_data.append({
                'session': session,
                'completion': session.progress_percentage or 0,
                'status': session.status,
                'course_name': session.course_integration_id.name if session.course_integration_id else 'N/A',
            })
        
        values = {
            'page_name': 'enrollments',
            'student': student,
            'enrollments': enrollment_data,
            'total_courses': len(sessions),
            'active_courses': len(sessions.filtered(lambda s: s.status == 'in_progress')),
            'completed_courses': len(sessions.filtered(lambda s: s.status == 'completed')),
        }
        
        return request.render('grants_training_suite_v19.portal_enrollments', values)
    
    @http.route(['/my/certificates/<int:cert_id>/download'], type='http', auth='user')
    def portal_certificate_download(self, cert_id, **kw):
        """Download certificate PDF"""
        student = self._get_student_for_portal_user()
        if not student:
            return request.redirect('/web/login')
        
        certificate = request.env['gr.certificate'].sudo().browse(cert_id)
        
        # Security check
        if certificate.student_id != student:
            return request.render('website.403')
        
        # Generate/return PDF
        try:
            pdf = request.env.ref('grants_training_suite_v19.action_report_certificate').sudo()._render_qweb_pdf([cert_id])[0]
            
            pdfhttpheaders = [
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(pdf)),
                ('Content-Disposition', f'attachment; filename="Certificate_{certificate.name}.pdf"')
            ]
            return request.make_response(pdf, headers=pdfhttpheaders)
        except Exception as e:
            _logger.error('Certificate download error: %s', str(e))
            return request.render('website.404')
    
    # DOCUMENT MANAGEMENT ROUTES MOVED TO student_documents_portal MODULE
    # Document request functionality is now handled by the student_documents_portal module
    # Routes: /my/documents, /my/documents/new, /my/documents/<id>
    
    # OLD REGISTRATION ROUTES REMOVED - Now using student_enrollment_portal module
    # Students should register at /student/register instead
    
    @http.route(['/grants/login'], type='http', auth='public', website=True, sitemap=False)
    def student_login(self, redirect=None, **kw):
        """Student login page (redirects to Odoo's login)"""
        # Use Odoo's built-in login mechanism
        return request.redirect('/web/login?redirect=/my/student')
    
    @http.route(['/grants/courses/catalog'], type='http', auth='public', website=True)
    def course_catalog(self, **kw):
        """Public course catalog page"""
        active_integrations = request.env['gr.course.integration'].sudo().search([
            ('status', '=', 'active')
        ])
        
        values = {
            'page_name': 'course_catalog',
            'courses': active_integrations,
        }
        
        return request.render('grants_training_suite_v19.portal_course_catalog', values)
    
    @http.route(['/grants/courses/<int:course_id>'], type='http', auth='public', website=True)
    def course_detail_public(self, course_id, **kw):
        """Public course detail page"""
        course = request.env['gr.course.integration'].sudo().browse(course_id)
        
        if not course.exists():
            return request.render('website.404')
        
        values = {
            'page_name': 'course_detail_public',
            'course': course,
        }
        
        return request.render('grants_training_suite_v19.portal_course_detail_public', values)
    
    # Course Enrollment Request Routes
    
    @http.route(['/my/available-courses'], type='http', auth='user', website=True)
    def portal_available_courses(self, **kw):
        """Available courses page for authenticated students"""
        student = self._get_student_for_portal_user()
        
        if not student:
            return request.render('grants_training_suite_v19.portal_no_student')
        
        # Get all active course integrations
        all_courses = request.env['gr.course.integration'].sudo().search([
            ('status', '=', 'active')
        ])
        
        # Get courses student is already enrolled in
        enrolled_course_ids = student.course_session_ids.mapped('course_integration_id').ids
        
        # Filter out enrolled courses
        available_courses = all_courses.filtered(lambda c: c.id not in enrolled_course_ids)
        
        # Get pending enrollment requests
        pending_requests = request.env['course.enrollment.request'].search([
            ('student_id', '=', student.id),
            ('state', 'in', ['draft', 'pending'])
        ])
        pending_course_ids = pending_requests.mapped('course_integration_id').ids
        
        values = {
            'page_name': 'available_courses',
            'student': student,
            'courses': available_courses,
            'pending_course_ids': pending_course_ids,
        }
        
        return request.render('grants_training_suite_v19.portal_available_courses', values)
    
    @http.route(['/my/courses/request/<int:course_id>'], type='http', auth='user', website=True)
    def portal_enrollment_request_form(self, course_id, **kw):
        """Enrollment request form"""
        student = self._get_student_for_portal_user()
        
        if not student:
            return request.render('grants_training_suite_v19.portal_no_student')
        
        course = request.env['gr.course.integration'].sudo().browse(course_id)
        
        if not course.exists() or course.status != 'active':
            return request.render('website.404')
        
        # Check if already enrolled
        existing_session = request.env['gr.course.session'].search([
            ('student_id', '=', student.id),
            ('course_integration_id', '=', course.id)
        ], limit=1)
        
        if existing_session:
            return request.render('grants_training_suite_v19.portal_enrollment_request_error', {
                'error': _('You are already enrolled in this course.')
            })
        
        # Check if already has pending request
        existing_request = request.env['course.enrollment.request'].search([
            ('student_id', '=', student.id),
            ('course_integration_id', '=', course.id),
            ('state', 'in', ['draft', 'pending'])
        ], limit=1)
        
        if existing_request:
            return request.render('grants_training_suite_v19.portal_enrollment_request_error', {
                'error': _('You already have a pending request for this course.')
            })
        
        values = {
            'page_name': 'enrollment_request',
            'student': student,
            'course': course,
        }
        
        return request.render('grants_training_suite_v19.portal_enrollment_request_form', values)
    
    @http.route(['/my/courses/request/submit'], type='http', auth='user', website=True, methods=['POST'], csrf=False)
    def portal_enrollment_request_submit(self, **post):
        """Handle enrollment request submission"""
        try:
            student = self._get_student_for_portal_user()
            
            if not student:
                return request.render('grants_training_suite_v19.portal_no_student')
            
            course_id = int(post.get('course_id'))
            course = request.env['gr.course.integration'].sudo().browse(course_id)
            
            if not course.exists():
                raise ValidationError(_('Invalid course selected.'))
            
            # Create enrollment request
            request_vals = {
                'student_id': student.id,
                'course_integration_id': course.id,
                'notes': post.get('notes', ''),
                'state': 'draft',
            }
            
            enrollment_request = request.env['course.enrollment.request'].create(request_vals)
            
            # Submit the request
            enrollment_request.action_submit()
            
            _logger.info(f'Enrollment request {enrollment_request.name} created and submitted by student {student.name}')
            
            return request.render('grants_training_suite_v19.portal_enrollment_request_success', {
                'request': enrollment_request,
                'student': student,
                'course': course,
            })
            
        except Exception as e:
            _logger.error(f'Enrollment request submission error: {str(e)}')
            return request.render('grants_training_suite_v19.portal_enrollment_request_error', {
                'error': _('Failed to submit enrollment request. Please try again or contact support.')
            })
    
    @http.route(['/my/enrollment-requests'], type='http', auth='user', website=True)
    def portal_my_enrollment_requests(self, **kw):
        """List of enrollment requests for student"""
        student = self._get_student_for_portal_user()
        
        if not student:
            return request.render('grants_training_suite_v19.portal_no_student')
        
        requests = request.env['course.enrollment.request'].search([
            ('student_id', '=', student.id)
        ], order='request_date desc')
        
        values = {
            'page_name': 'enrollment_requests',
            'student': student,
            'requests': requests,
        }
        
        return request.render('grants_training_suite_v19.portal_my_enrollment_requests', values)
