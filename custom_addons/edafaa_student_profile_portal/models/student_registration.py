from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

# OP#352 — map registration workflow state → profile application_status
REGISTRATION_STATE_TO_APPLICATION_STATUS = {
    'approved': 'accepted',
    'enrolled': 'accepted',
    'rejected': 'rejected',
    'draft': 'under_review',
    'submitted': 'under_review',
    'eligibility_review': 'under_review',
    'document_review': 'under_review',
}


class StudentRegistration(models.Model):
    _inherit = 'student.registration'

    id_number = fields.Char(
        string='رقم الهوية',
        tracking=True,
    )
    street = fields.Char(
        string='الشارع',
        tracking=True,
    )
    city = fields.Char(
        string='المدينة',
        tracking=True,
    )
    country_id = fields.Many2one(
        'res.country',
        string='الدولة',
        tracking=True,
    )
    specialization_id = fields.Many2one(
        'op.program',
        string='التخصص',
        tracking=True,
    )

    @api.model
    def _map_registration_state_to_application_status(self, state):
        return REGISTRATION_STATE_TO_APPLICATION_STATUS.get(state, 'under_review')

    def _find_linked_op_student(self):
        """Resolve linked op.student (registration_number or email)."""
        self.ensure_one()
        Student = self.env['op.student']
        if self.name:
            student = Student.search([('registration_number', '=', self.name)], limit=1)
            if student:
                return student
        if self.email:
            return Student.search([('email', '=', self.email)], limit=1)
        return Student

    def _sync_op_student_application_status(self):
        for reg in self:
            student = reg._find_linked_op_student()
            if not student:
                continue
            status = reg._map_registration_state_to_application_status(reg.state)
            if student.application_status != status:
                student.write({'application_status': status})

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals:
            self._sync_op_student_application_status()
        return res

    def _validate_registration_profile_for_student(self):
        """Ensure registration has all data required by Step 3 before op.student create."""
        self.ensure_one()
        field_checks = [
            ('student_name_arabic', _('Arabic Name')),
            ('student_name_english', _('English Name')),
            ('id_number', _('رقم الهوية')),
            ('email', _('Email')),
            ('phone', _('رقم الهاتف')),
            ('street', _('الشارع')),
            ('city', _('المدينة')),
        ]
        missing = []
        for field_name, label in field_checks:
            value = self[field_name]
            if not value or not str(value).strip():
                missing.append(label)
        if not self.birth_date:
            missing.append(_('Birth Date'))
        if not self.country_id:
            missing.append(_('الدولة'))
        if missing:
            raise ValidationError(
                _('Cannot create student record. Missing required profile field(s): %s')
                % ', '.join(missing)
            )

    def _prepare_student_profile_vals(self, partner, name_english, first_name, last_name):
        """Build op.student vals from registration profile fields."""
        self.ensure_one()
        gender_map = {
            'male': 'm',
            'female': 'f',
        }
        nationality_country = self.env['res.country'].search(
            [('name', 'ilike', self.nationality)], limit=1,
        ) if self.nationality else self.env['res.country']

        return {
            'name_arabic': self.student_name_arabic.strip(),
            'name_english': name_english,
            'name': name_english,
            'first_name': first_name,
            'last_name': last_name,
            'partner_id': partner.id,
            'email': self.email,
            'phone': self.phone,
            'birth_date': self.birth_date,
            'gender': gender_map.get(self.gender, 'm'),
            'id_number': self.id_number.strip(),
            'street': self.street.strip(),
            'city': self.city.strip(),
            'country_id': self.country_id.id,
            'nationality': nationality_country.id if nationality_country else False,
            'specialization_id': self.specialization_id.id if self.specialization_id else False,
            'has_previous_certificate': self.has_previous_certificate,
            'certificate_type': self.certificate_type or False,
            'registration_number': self.name,
            'source_type': 'student_registration',
            'application_status': self._map_registration_state_to_application_status(self.state),
        }

    def _create_student_record(self):
        """Create or update op.student with full Step 3 profile mapping from registration."""
        self.ensure_one()
        self._validate_registration_profile_for_student()

        name_english = self.student_name_english.strip()
        first_name, last_name = self.env['op.student']._split_english_name(name_english)

        partner = self.env['res.partner'].search([('email', '=', self.email)], limit=1)
        partner_vals = {
            'name': name_english,
            'email': self.email,
            'phone': self.phone,
            'street': self.street,
            'city': self.city,
            'country_id': self.country_id.id,
            'is_company': False,
        }
        if 'id_number' in self.env['res.partner']._fields:
            partner_vals['id_number'] = self.id_number.strip()
        if not partner:
            partner = self.env['res.partner'].create(partner_vals)
        else:
            partner.write(partner_vals)

        student_vals = self._prepare_student_profile_vals(
            partner, name_english, first_name, last_name,
        )

        existing_student = self.env['op.student'].search([('email', '=', self.email)], limit=1)
        if existing_student:
            existing_student.write(student_vals)
            _logger.info(
                'Updated op.student %s from registration %s via profile portal bridge',
                existing_student.id,
                self.name,
            )
            return existing_student

        student = self.env['op.student'].create(student_vals)
        _logger.info(
            'Created op.student %s from registration %s via profile portal bridge',
            student.id,
            self.name,
        )
        return student
