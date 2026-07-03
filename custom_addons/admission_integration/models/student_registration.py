# -*- coding: utf-8 -*-

import logging
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StudentRegistration(models.Model):
    _inherit = 'student.registration'

    # Link to admission record
    source_admission_id = fields.Many2one(
        'op.admission',
        string='Admission Record',
        readonly=True,
        tracking=True,
        help='Admission record created from this registration'
    )

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

    def action_create_admission(self):
        """Create op.admission record from approved registration"""
        self.ensure_one()
        
        if self.state != 'approved':
            raise UserError(_('Only approved registrations can create admission records.'))
        
        # Check if admission already exists
        if self.source_admission_id:
            raise UserError(_('Admission record already exists for this registration. Please check the admission record.'))
        
        existing_admission = self.env['op.admission'].search([
            ('source_registration_id', '=', self.id)
        ], limit=1)
        
        if existing_admission:
            self.write({'source_admission_id': existing_admission.id})
            raise UserError(_('Admission record already exists: %s') % existing_admission.application_number)
        
        # Get default admission register
        admission_register = self._get_default_admission_register()
        
        # Get default course - try from register first, then get any active course
        course_id = False
        if admission_register.course_id:
            course_id = admission_register.course_id.id
        else:
            # Get first active course as default
            default_course = self.env['op.course'].search([
                ('active', '=', True)
            ], limit=1)
            if default_course:
                course_id = default_course.id
            else:
                # If no course exists, we'll need to let user set it manually
                # For now, we'll raise an error with helpful message
                raise UserError(_(
                    'No course found. Please create at least one course in OpenEduCat '
                    'or set a default course in the Admission Register before creating admissions.'
                ))
        
        # Split name into first/last
        name_parts = self.student_name_english.strip().split(' ', 1)
        first_name = name_parts[0] if name_parts else self.student_name_english
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Map gender
        gender_map = {'male': 'm', 'female': 'f'}
        gender = gender_map.get(self.gender, 'm')
        
        # Address country from registration (not nationality text)
        country_id = self.country_id.id if self.country_id else False
        nationality_country = self.env['res.country']
        if self.nationality:
            nationality_country = self.env['res.country'].search([
                ('name', 'ilike', self.nationality)
            ], limit=1)

        admission_vals = {
            'name': self.student_name_english,
            'first_name': first_name,
            'last_name': last_name,
            'email': self.email,
            'phone': self.phone,
            'birth_date': self.birth_date,
            'gender': gender,
            'street': self.street or False,
            'city': self.city or False,
            'country_id': country_id,
            'id_number': getattr(self, 'id_number', False) or False,
            'nationality': nationality_country.id if nationality_country else False,
            'specialization_id': getattr(self, 'specialization_id', False) and self.specialization_id.id or False,
            'course_id': course_id,
            'register_id': admission_register.id,
            'source_type': 'student_registration',
            'source_registration_id': self.id,
            'is_imported': True,
            'state': 'submit',
            'application_date': fields.Datetime.now(),
        }
        
        admission = self.env['op.admission'].create(admission_vals)
        
        # Link admission back to registration
        self.write({'source_admission_id': admission.id})
        
        self.message_post(
            body=_('Admission record created: %s') % admission.application_number,
            message_type='notification'
        )
        
        _logger.info(f'Created admission {admission.application_number} from registration {self.name}')
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Admission Record'),
            'res_model': 'op.admission',
            'res_id': admission.id,
            'view_mode': 'form',
            'target': 'current',
        }

