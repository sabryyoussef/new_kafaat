# -*- coding: utf-8 -*-

import base64
import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)


class StudentDocumentsPortal(CustomerPortal):
    """Student Documents Portal Controller"""
    
    def _get_student_for_portal_user(self):
        """Get student record for current portal user"""
        if not request.env.user or request.env.user._is_public():
            return False
        
        # Find student by email matching portal user email
        student = request.env['gr.student'].sudo().search([
            ('email', '=', request.env.user.email)
        ], limit=1)
        
        return student
    
    @http.route(['/my/documents'], type='http', auth='user', website=True)
    def portal_my_documents(self, **kw):
        """List all document requests"""
        student = self._get_student_for_portal_user()
        if not student:
            return request.render('student_documents_portal.portal_no_student')
        
        doc_requests = request.env['gr.document.request.portal'].search([
            ('student_id', '=', student.id)
        ], order='create_date desc')
        
        values = {
            'page_name': 'documents',
            'student': student,
            'document_requests': doc_requests,
        }
        return request.render('student_documents_portal.portal_documents', values)
    
    @http.route(['/my/documents/new'], type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=False)
    def portal_document_request_new(self, **kw):
        """Create new document request"""
        student = self._get_student_for_portal_user()
        if not student:
            return request.render('student_documents_portal.portal_no_student')
        
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
                return request.render('student_documents_portal.portal_document_request_form', {
                    'page_name': 'new_document_request',
                    'student': student,
                    'error': _('Failed to create document request. Please try again.')
                })
        
        values = {
            'page_name': 'new_document_request',
            'student': student,
        }
        return request.render('student_documents_portal.portal_document_request_form', values)
    
    @http.route(['/my/documents/<int:request_id>'], type='http', auth='user', website=True)
    def portal_document_detail(self, request_id, **kw):
        """Document request detail page"""
        student = self._get_student_for_portal_user()
        if not student:
            return request.render('student_documents_portal.portal_no_student')
        
        doc_request = request.env['gr.document.request.portal'].sudo().browse(request_id)
        
        # Security check - verify this request belongs to the student
        if doc_request.student_id != student:
            return request.render('website.403')
        
        values = {
            'page_name': 'document_detail',
            'student': student,
            'request': doc_request,
        }
        
        return request.render('student_documents_portal.portal_document_detail', values)

