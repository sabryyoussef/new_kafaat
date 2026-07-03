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
    sibling_ids = fields.Many2many(
        'op.student',
        string='Siblings',
        compute='_compute_sibling_ids',
        help='Other students sharing at least one linked parent.',
    )
    training_status = fields.Selection(
        selection=[
            ('new', 'New Trainee'),
            ('active', 'Currently Registered'),
            ('completed', 'Completed'),
        ],
        string='Training Status',
        compute='_compute_training_summary',
        help='Derived from course enrollments (course_detail_ids).',
    )
    current_course_id = fields.Many2one(
        'op.course',
        string='Current Course',
        compute='_compute_training_summary',
        help='Primary running enrollment: highest ID among running enrollments.',
    )
    current_batch_id = fields.Many2one(
        'op.batch',
        string='Current Batch',
        compute='_compute_training_summary',
        help='Batch from the primary running enrollment.',
    )
    running_course_count = fields.Integer(
        string='Running Courses',
        compute='_compute_training_summary',
    )
    completed_course_count = fields.Integer(
        string='Completed Courses',
        compute='_compute_training_summary',
    )
    certificate_ids = fields.One2many(
        'edafaa.student.certificate',
        'student_id',
        string='Course Certificates',
    )
    certificate_count = fields.Integer(
        string='Certificates',
        compute='_compute_certificate_count',
    )

    @api.depends('certificate_ids')
    def _compute_certificate_count(self):
        for student in self:
            student.certificate_count = len(student.certificate_ids)

    def action_view_certificates(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Certificates'),
            'res_model': 'edafaa.student.certificate',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
        }

    @api.depends(
        'course_detail_ids',
        'course_detail_ids.state',
        'course_detail_ids.course_id',
        'course_detail_ids.batch_id',
    )
    def _compute_training_summary(self):
        """Summarize training lifecycle from op.student.course enrollments."""
        for student in self:
            enrollments = student.course_detail_ids
            running = enrollments.filtered(lambda e: e.state == 'running')
            finished = enrollments.filtered(lambda e: e.state == 'finished')

            student.running_course_count = len(running)
            student.completed_course_count = len(finished)

            if not enrollments:
                student.training_status = 'new'
            elif running:
                student.training_status = 'active'
            elif finished:
                student.training_status = 'completed'
            else:
                # Enrollments exist but none use known running/finished states.
                student.training_status = 'new'

            if running:
                primary = running.sorted('id', reverse=True)[:1]
                student.current_course_id = primary.course_id
                student.current_batch_id = primary.batch_id
            else:
                student.current_course_id = False
                student.current_batch_id = False

    @api.depends('parent_ids', 'parent_ids.student_ids')
    def _compute_sibling_ids(self):
        for student in self:
            if student.parent_ids:
                student.sibling_ids = student.parent_ids.mapped('student_ids') - student
            else:
                student.sibling_ids = False

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
