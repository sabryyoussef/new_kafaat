# -*- coding: utf-8 -*-
"""
Public Demo Portal - All routes accessible without login for demonstration
WARNING: This is for DEMO/TESTING only. DO NOT use in production.
"""

import logging
from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class PublicDemoPortal(http.Controller):
    """Public Demo Portal - No authentication required"""
    
    @http.route(['/demo/test'], type='http', auth='public', website=True, sitemap=False)
    def demo_test(self, **kw):
        """Simple test route to verify controller is loaded"""
        return "<h1>Demo Controller is Working!</h1><p>If you see this, the controller is loaded.</p><a href='/demo'>Go to Demo Index</a>"
    
    def _get_demo_student(self):
        """Get or create a demo student for public viewing"""
        # Try to get the first student with demo data
        student = request.env['gr.student'].sudo().search([
            ('name', 'ilike', 'demo')
        ], limit=1)
        
        if not student:
            # Get any student
            student = request.env['gr.student'].sudo().search([], limit=1)
        
        return student
    
    @http.route(['/demo/student'], type='http', auth='public', website=True)
    def demo_student_dashboard(self, **kw):
        """Public demo student dashboard"""
        student = self._get_demo_student()
        
        if not student:
            return request.render('grants_training_suite_v19.demo_no_data', {
                'message': _('No demo student data available. Please install demo data.')
            })
        
        # Get enrollment requests
        enrollment_requests = request.env['course.enrollment.request'].sudo().search([
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
            'page_name': 'demo_student_dashboard',
            'student': student,
            'courses': student.course_session_ids,
            'progress': student.progress_percentage,
            'certificates': student.certificate_ids,
            'enrollment_requests': enrollment_requests,
            'pending_requests': pending_requests,
            'available_courses': available_courses,
            'is_demo': True,
        }
        
        return request.render('grants_training_suite_v19.portal_student_dashboard', values)
    
    @http.route(['/demo/courses'], type='http', auth='public', website=True)
    def demo_my_courses(self, **kw):
        """Public demo courses list"""
        student = self._get_demo_student()
        
        if not student:
            return request.render('grants_training_suite_v19.demo_no_data', {
                'message': _('No demo data available.')
            })
        
        values = {
            'page_name': 'demo_my_courses',
            'student': student,
            'sessions': student.course_session_ids,
            'is_demo': True,
        }
        
        return request.render('grants_training_suite_v19.portal_my_courses', values)
    
    @http.route(['/demo/courses/<int:session_id>'], type='http', auth='public', website=True)
    def demo_course_detail(self, session_id, **kw):
        """Public demo course detail"""
        session = request.env['gr.course.session'].sudo().browse(session_id)
        
        if not session.exists():
            return request.render('website.404')
        
        values = {
            'page_name': 'demo_course_detail',
            'student': session.student_id,
            'session': session,
            'is_demo': True,
        }
        
        return request.render('grants_training_suite_v19.portal_course_detail', values)
    
    @http.route(['/demo/certificates'], type='http', auth='public', website=True)
    def demo_my_certificates(self, **kw):
        """Public demo certificates"""
        student = self._get_demo_student()
        
        if not student:
            return request.render('grants_training_suite_v19.demo_no_data', {
                'message': _('No demo data available.')
            })
        
        values = {
            'page_name': 'demo_my_certificates',
            'student': student,
            'certificates': student.certificate_ids,
            'is_demo': True,
        }
        
        return request.render('grants_training_suite_v19.portal_my_certificates', values)
    
    @http.route(['/demo/available-courses'], type='http', auth='public', website=True)
    def demo_available_courses(self, **kw):
        """Public demo available courses"""
        student = self._get_demo_student()
        
        if not student:
            return request.render('grants_training_suite_v19.demo_no_data', {
                'message': _('No demo data available.')
            })
        
        # Get all active course integrations
        all_courses = request.env['gr.course.integration'].sudo().search([
            ('status', '=', 'active')
        ])
        
        # Get courses student is already enrolled in
        enrolled_course_ids = student.course_session_ids.mapped('course_integration_id').ids
        
        # Filter out enrolled courses
        available_courses = all_courses.filtered(lambda c: c.id not in enrolled_course_ids)
        
        # Get pending enrollment requests
        pending_requests = request.env['course.enrollment.request'].sudo().search([
            ('student_id', '=', student.id),
            ('state', 'in', ['draft', 'pending'])
        ])
        pending_course_ids = pending_requests.mapped('course_integration_id').ids
        
        values = {
            'page_name': 'demo_available_courses',
            'student': student,
            'courses': available_courses,
            'pending_course_ids': pending_course_ids,
            'is_demo': True,
        }
        
        return request.render('grants_training_suite_v19.portal_available_courses', values)
    
    @http.route(['/demo/enrollment-requests'], type='http', auth='public', website=True)
    def demo_my_enrollment_requests(self, **kw):
        """Public demo enrollment requests"""
        student = self._get_demo_student()
        
        if not student:
            return request.render('grants_training_suite_v19.demo_no_data', {
                'message': _('No demo data available.')
            })
        
        requests = request.env['course.enrollment.request'].sudo().search([
            ('student_id', '=', student.id)
        ], order='request_date desc')
        
        values = {
            'page_name': 'demo_enrollment_requests',
            'student': student,
            'requests': requests,
            'is_demo': True,
        }
        
        return request.render('grants_training_suite_v19.portal_my_enrollment_requests', values)
    
    @http.route(['/demo/documents'], type='http', auth='public', website=True)
    def demo_my_documents(self, **kw):
        """Public demo documents"""
        student = self._get_demo_student()
        
        if not student:
            return request.render('grants_training_suite_v19.demo_no_data', {
                'message': _('No demo data available.')
            })
        
        doc_requests = request.env['gr.document.request.portal'].sudo().search([
            ('student_id', '=', student.id)
        ], order='create_date desc')
        
        values = {
            'page_name': 'demo_documents',
            'student': student,
            'document_requests': doc_requests,
            'is_demo': True,
        }
        
        return request.render('student_documents_portal.portal_documents', values)
    
    @http.route(['/demo/registration'], type='http', auth='public', website=True)
    def demo_my_registration(self, **kw):
        """Public demo registration status"""
        # Get a demo registration
        registration = request.env['student.registration'].sudo().search([
            ('state', '!=', 'enrolled')
        ], limit=1, order='create_date desc')
        
        if not registration:
            return request.render('grants_training_suite_v19.demo_no_data', {
                'message': _('No demo registration data available.')
            })
        
        values = {
            'registration': registration,
            'page_name': 'demo_registration',
            'is_demo': True,
        }
        
        return request.render('student_enrollment_portal.portal_my_registration', values)
    
    @http.route(['/demo', '/demo/'], type='http', auth='public', website=True, sitemap=False)
    def demo_index(self, **kw):
        """Demo portal index with links to all demo pages"""
        try:
            student = self._get_demo_student()
            
            values = {
                'page_name': 'demo_index',
                'student': student,
            }
            
            return request.render('grants_training_suite_v19.demo_portal_index', values)
        except Exception as e:
            _logger.error('Demo portal error: %s', str(e))
            import traceback
            _logger.error(traceback.format_exc())
            # Return simple HTML with error info
            return f"""
            <html>
                <body>
                    <h1>Demo Portal Error</h1>
                    <p>Error: {str(e)}</p>
                    <p>Check Odoo logs for details.</p>
                    <p><a href="/demo/test">Test Route</a></p>
                </body>
            </html>
            """

