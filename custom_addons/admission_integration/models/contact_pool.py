# -*- coding: utf-8 -*-

import logging
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ContactPool(models.Model):
    _inherit = 'contact.pool'

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

    def action_create_admissions_from_contacts(self):
        """Create op.admission records for eligible contacts in pool"""
        self.ensure_one()
        
        if not self.contact_ids:
            raise UserError(_('No contacts in this pool.'))
        
        # Get default admission register
        admission_register = self._get_default_admission_register()
        
        # Filter eligible contacts (not companies, have email)
        eligible_contacts = self.contact_ids.filtered(
            lambda c: not c.is_company and c.email
        )
        
        if not eligible_contacts:
            raise UserError(_('No eligible contacts found in this pool. Contacts must have an email address and not be a company.'))
        
        created_admissions = self.env['op.admission']
        skipped_count = 0
        
        for contact in eligible_contacts:
            # Check if contact is already a student
            existing_student = self.env['op.student'].search([
                ('partner_id', '=', contact.id)
            ], limit=1)
            
            if existing_student:
                _logger.info(f'Contact {contact.name} is already a student, skipping')
                skipped_count += 1
                continue
            
            # Check if admission already exists
            existing_admission = self.env['op.admission'].search([
                ('source_contact_pool_id', '=', self.id),
                ('source_contact_id', '=', contact.id)
            ], limit=1)
            
            if existing_admission:
                _logger.warning(f'Admission already exists for contact {contact.name}: {existing_admission.application_number}')
                skipped_count += 1
                continue
            
            # Split name
            name_parts = contact.name.strip().split(' ', 1)
            first_name = name_parts[0] if name_parts else contact.name
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
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
                    # Skip this contact if no course available
                    _logger.warning(f'No course found, skipping contact {contact.name}')
                    skipped_count += 1
                    continue
            
            # Create admission record
            admission_vals = {
                'name': contact.name,
                'first_name': first_name,
                'last_name': last_name,
                'email': contact.email or '',
                'phone': contact.phone or contact.mobile or '',
                'birth_date': False,  # May not be available
                'gender': 'm',  # Default, can be updated
                'street': contact.street or '',
                'street2': contact.street2 or '',
                'city': contact.city or '',
                'zip': contact.zip or '',
                'country_id': contact.country_id.id if contact.country_id else False,
                'state_id': contact.state_id.id if contact.state_id else False,
                'course_id': course_id,  # Required field
                'register_id': admission_register.id,
                'source_type': 'contact_pool',
                'source_contact_pool_id': self.id,
                'source_contact_id': contact.id,
                'is_imported': True,
                'state': 'draft',  # Start at draft for manual review
                'application_date': fields.Datetime.now(),
            }
            
            admission = self.env['op.admission'].create(admission_vals)
            created_admissions += admission
            _logger.info(f'Created admission {admission.application_number} for contact {contact.name}')
        
        message = _('Created %d admission record(s) from pool contacts.') % len(created_admissions)
        if skipped_count > 0:
            message += _(' %d contact(s) were skipped (already students or have admissions).') % skipped_count
        
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
            raise UserError(_('No new admissions created. All contacts were skipped.'))

