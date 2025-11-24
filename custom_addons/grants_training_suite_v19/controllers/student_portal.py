# -*- coding: utf-8 -*-

import base64
import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

_logger = logging.getLogger(__name__)


class StudentPortal(CustomerPortal):
    """Student Portal Controller"""
    
    def _prepare_home_portal_values(self, counters):
        """Add student-related counters to portal home"""
        values = super()._prepare_home_portal_values(counters)
        
        if 'course_count' in counters:
            student = self._get_student_for_portal_user()
            if student:
                values['course_count'] = len(student.course_session_ids)
        
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
        
        values = {
            'page_name': 'student_dashboard',
            'student': student,
            'courses': student.course_session_ids,
            'progress': student.progress_percentage,
            'certificates': student.certificate_ids,
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
    
    @http.route(['/my/documents'], type='http', auth='user', website=True)
    def portal_my_documents(self, **kw):
        """List all document requests"""
        student = self._get_student_for_portal_user()
        if not student:
            return request.render('grants_training_suite_v19.portal_no_student')
        
        doc_requests = request.env['gr.document.request.portal'].search([
            ('student_id', '=', student.id)
        ], order='create_date desc')
        
        values = {
            'page_name': 'documents',
            'student': student,
            'document_requests': doc_requests,
        }
        return request.render('grants_training_suite_v19.portal_documents', values)
    
    @http.route(['/my/documents/new'], type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=False)
    def portal_document_request_new(self, **kw):
        """Create new document request"""
        student = self._get_student_for_portal_user()
        if not student:
            return request.render('grants_training_suite_v19.portal_no_student')
        
        if request.httprequest.method == 'POST':
            try:
                # Create document request
                vals = {
                    'student_id': student.id,
                    'request_type': kw.get('request_type'),
                    'document_type': kw.get('document_type'),
                    'description': kw.get('description'),
                    'status': 'submitted',
                }
                doc_request = request.env['gr.document.request.portal'].sudo().create(vals)
                
                # Handle file upload if present
                uploaded_file = request.httprequest.files.get('file')
                if uploaded_file and uploaded_file.filename:
                    file_content = uploaded_file.read()
                    attachment = request.env['ir.attachment'].sudo().create({
                        'name': uploaded_file.filename,
                        'datas': base64.b64encode(file_content),
                        'res_model': 'gr.document.request.portal',
                        'res_id': doc_request.id,
                    })
                    doc_request.attachment_ids = [(4, attachment.id)]
                
                return request.redirect('/my/documents')
            except Exception as e:
                _logger.error('Document request creation error: %s', str(e))
                return request.render('grants_training_suite_v19.portal_document_request_form', {
                    'page_name': 'new_document_request',
                    'student': student,
                    'error': _('Failed to create document request. Please try again.')
                })
        
        values = {
            'page_name': 'new_document_request',
            'student': student,
        }
        return request.render('grants_training_suite_v19.portal_document_request_form', values)
    
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
