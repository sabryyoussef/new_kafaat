from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpStudent(models.Model):
    _inherit = 'op.student'

    name_arabic = fields.Char(
        string='Arabic Name',
        required=True,
        tracking=True,
    )
    name_english = fields.Char(
        string='English Name',
        required=True,
        tracking=True,
    )

    @api.onchange('name_english')
    def _onchange_name_english(self):
        if self.name_english:
            self._sync_english_name_to_parts(self.name_english.strip())

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._validate_required_profile_vals(vals)
            if vals.get('name_english') and str(vals['name_english']).strip():
                self._apply_english_name_vals(vals)
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('name_english'):
            self._apply_english_name_vals(vals)
        return super().write(vals)

    def _apply_english_name_vals(self, vals):
        """Sync delegated name and OpenEduCat name parts from English full name."""
        name_english = str(vals['name_english']).strip()
        vals['name'] = name_english
        first_name, last_name = self._split_english_name(name_english)
        vals['first_name'] = first_name
        vals['last_name'] = last_name

    def _sync_english_name_to_parts(self, name_english):
        self.name = name_english
        first_name, last_name = self._split_english_name(name_english)
        self.first_name = first_name
        self.last_name = last_name

    @api.model
    def _split_english_name(self, name_english):
        """Conservative split: first whitespace-separated token = first_name, rest = last_name."""
        name_english = (name_english or '').strip()
        if not name_english:
            return '', ''
        parts = name_english.split(None, 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        return first_name, last_name

    @api.model
    def _validate_required_profile_vals(self, vals):
        """Raise ValidationError before ORM insert when required profile data is missing."""
        field_checks = [
            ('name_arabic', _('Arabic Name')),
            ('name_english', _('English Name')),
            ('id_number', _('ID Number')),
            ('email', _('Email')),
            ('phone', _('Phone')),
            ('street', _('Street')),
            ('city', _('City')),
        ]
        missing = []
        for field_name, label in field_checks:
            if field_name not in vals:
                missing.append(label)
                continue
            value = vals[field_name]
            if not value or not str(value).strip():
                missing.append(label)
        if 'birth_date' not in vals or not vals.get('birth_date'):
            missing.append(_('Birth Date'))
        if 'country_id' not in vals or not vals.get('country_id'):
            missing.append(_('Country'))
        if missing:
            raise ValidationError(
                _('Missing required student profile field(s): %s')
                % ', '.join(missing)
            )

    @api.constrains(
        'name_arabic', 'name_english', 'id_number', 'birth_date',
        'email', 'phone', 'street', 'city', 'country_id',
    )
    def _check_required_profile_fields(self):
        field_checks = [
            ('name_arabic', _('Arabic Name')),
            ('name_english', _('English Name')),
            ('id_number', _('ID Number')),
            ('email', _('Email')),
            ('phone', _('Phone')),
            ('street', _('Street')),
            ('city', _('City')),
        ]
        for student in self:
            missing = []
            for field_name, label in field_checks:
                value = student[field_name]
                if not value or not str(value).strip():
                    missing.append(label)
            if not student.birth_date:
                missing.append(_('Birth Date'))
            if not student.country_id:
                missing.append(_('Country'))
            if missing:
                raise ValidationError(
                    _('Missing required student profile field(s): %s')
                    % ', '.join(missing)
                )
