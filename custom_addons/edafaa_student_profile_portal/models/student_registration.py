from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class StudentRegistration(models.Model):
    _inherit = 'student.registration'

    id_number = fields.Char(
        string='ID Number',
        tracking=True,
    )
    street = fields.Char(
        string='Street',
        tracking=True,
    )
    city = fields.Char(
        string='City',
        tracking=True,
    )
    country_id = fields.Many2one(
        'res.country',
        string='Country',
        tracking=True,
    )

    def _validate_registration_profile_for_student(self):
        """Ensure registration has all data required by Step 3 before op.student create."""
        self.ensure_one()
        field_checks = [
            ('student_name_arabic', _('Arabic Name')),
            ('student_name_english', _('English Name')),
            ('id_number', _('ID Number')),
            ('email', _('Email')),
            ('phone', _('Phone')),
            ('street', _('Street')),
            ('city', _('City')),
        ]
        missing = []
        for field_name, label in field_checks:
            value = self[field_name]
            if not value or not str(value).strip():
                missing.append(label)
        if not self.birth_date:
            missing.append(_('Birth Date'))
        if not self.country_id:
            missing.append(_('Country'))
        if missing:
            raise ValidationError(
                _('Cannot create student record. Missing required profile field(s): %s')
                % ', '.join(missing)
            )

    def _create_student_record(self):
        """Create op.student with full Step 3 profile mapping from registration."""
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
        if not partner:
            partner = self.env['res.partner'].create(partner_vals)
        else:
            partner.write(partner_vals)

        existing_student = self.env['op.student'].search([('email', '=', self.email)], limit=1)
        if existing_student:
            _logger.warning(
                'Student with email %s already exists: %s',
                self.email,
                existing_student.id,
            )
            return existing_student

        gender_map = {
            'male': 'm',
            'female': 'f',
        }
        nationality_country = self.env['res.country'].search(
            [('name', 'ilike', self.nationality)], limit=1,
        ) if self.nationality else self.env['res.country']

        student_vals = {
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
        }

        student = self.env['op.student'].create(student_vals)
        _logger.info(
            'Created op.student %s from registration %s via profile portal bridge',
            student.id,
            self.name,
        )
        return student
