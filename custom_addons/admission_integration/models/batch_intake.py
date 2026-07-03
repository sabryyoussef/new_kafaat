# -*- coding: utf-8 -*-

import logging
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BatchIntake(models.Model):
    _inherit = 'batch.intake'

    def _get_default_admission_register(self):
        """Get or create default admission register"""
        # Try to find active admission register
        register = self.env['op.admission.register'].search([
            ('active', '=', True),
            ('start_date', '<=', fields.Date.today()),
            ('end_date', '>=', fields.Date.today())
        ], limit=1, order='start_date desc')
        
        if not register:
            # Get any active register
            register = self.env['op.admission.register'].search([
                ('active', '=', True)
            ], limit=1, order='start_date desc')
        
        if not register:
            # Create default register if none exists
            register = self.env['op.admission.register'].create({
                'name': 'Default Admission Register %s' % fields.Date.today().year,
                'start_date': fields.Date.today(),
                'end_date': fields.Date.today() + relativedelta(years=1),
                'active': True,
            })
            _logger.info(f'Created default admission register: {register.name}')
        
        return register

    def action_create_admissions_from_students(self):
        """Create op.admission records for all students in this batch intake"""
        self.ensure_one()
        
        if self.state != 'processed':
            raise UserError(_('Batch intake must be processed before creating admissions.'))
        
        if not self.openeducat_student_ids:
            raise UserError(_('No students found in this batch intake.'))
        
        # Get default admission register
        admission_register = self._get_default_admission_register()
        
        created_admissions = self.env['op.admission']
        skipped_count = 0
        
        for student in self.openeducat_student_ids:
            # Check if admission already exists
            existing_admission = self.env['op.admission'].search([
                ('source_batch_intake_id', '=', self.id),
                ('email', '=', student.email)
            ], limit=1)
            
            if existing_admission:
                _logger.warning(f'Admission already exists for student {student.name}: {existing_admission.application_number}')
                skipped_count += 1
                continue
            
            # Get course - from batch intake first, then register, then default
            course_id = False
            if self.course_id:
                course_id = self.course_id.id
            elif admission_register.course_id:
                course_id = admission_register.course_id.id
            else:
                # Get first active course as default
                default_course = self.env['op.course'].search([
                    ('active', '=', True)
                ], limit=1)
                if default_course:
                    course_id = default_course.id
                else:
                    # Skip this student if no course available
                    _logger.warning(f'No course found, skipping student {student.name}')
                    skipped_count += 1
                    continue
            
            # Create admission record
            admission_vals = {
                'name': student.name,
                'first_name': student.first_name or student.name.split()[0] if student.name else '',
                'last_name': student.last_name or ' '.join(student.name.split()[1:]) if student.name and len(student.name.split()) > 1 else '',
                'email': student.email or '',
                'phone': student.phone or '',
                'birth_date': student.birth_date or False,
                'gender': student.gender or 'm',
                'street': student.street or False,
                'city': student.city or False,
                'country_id': student.country_id.id if student.country_id else False,
                'id_number': student.id_number or False,
                'nationality': student.nationality.id if student.nationality else False,
                'specialization_id': student.specialization_id.id if getattr(student, 'specialization_id', False) else False,
                'course_id': course_id,  # Required field
                'batch_id': self.batch_id.id if self.batch_id else False,
                'register_id': admission_register.id,
                'source_type': 'batch_intake',
                'source_batch_intake_id': self.id,
                'is_imported': True,
                'state': 'submit',
                'application_date': fields.Datetime.now(),
            }
            
            admission = self.env['op.admission'].create(admission_vals)
            created_admissions += admission
            _logger.info(f'Created admission {admission.application_number} for student {student.name}')
        
        message = _('Created %d admission record(s) from batch intake students.') % len(created_admissions)
        if skipped_count > 0:
            message += _(' %d student(s) already had admission records.') % skipped_count
        
        self.message_post(
            body=message,
            message_type='notification'
        )
        
        if created_admissions:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Created Admissions'),
                'res_model': 'op.admission',
                'view_mode': 'list,form',
                'domain': [('id', 'in', created_admissions.ids)],
                'target': 'current',
            }
        else:
            raise UserError(_('No new admissions created. All students already have admission records.'))

