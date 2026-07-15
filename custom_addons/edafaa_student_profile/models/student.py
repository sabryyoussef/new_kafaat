from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpStudent(models.Model):
    _inherit = 'op.student'
    _rec_names_search = ['name', 'id_number', 'name_arabic', 'name_english']

    id_number = fields.Char(string='رقم الهوية', size=64)
    voucher_number = fields.Char(
        string='رقم قسيمة الاختبار',
        size=64,
        index=True,
        help='Exam / test voucher number',
    )
    application_status = fields.Selection(
        selection=[
            ('accepted', 'مقبول'),
            ('rejected', 'مرفوض'),
            ('under_review', 'تحت المراجعة'),
            ('cancelled', 'ملغي'),
        ],
        string='حالة الطالب',
        default='under_review',
        tracking=True,
        index=True,
        help='Admission / application status on the student profile '
             '(distinct from training_status).',
    )
    assigned_user_id = fields.Many2one(
        'res.users',
        string='موظف المبيعات المسؤول',
        tracking=True,
        index=True,
        help='Sales staff responsible for this trainee (Excel bulk assign).',
    )

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
    specialization_id = fields.Many2one(
        'op.program',
        string='التخصص',
        tracking=True,
        help='Training program / specialization (التخصص).',
    )
    registration_number = fields.Char(
        string='رقم التسجيل',
        readonly=True,
        tracking=True,
        copy=False,
        help='Registration number from student.registration when created via portal.',
    )
    source_type = fields.Selection(
        selection=[
            ('manual', 'Manual Entry'),
            ('student_registration', 'Student Registration Portal'),
            ('batch_intake', 'Batch Intake'),
            ('contact_pool', 'Contact Pool Manager'),
        ],
        string='نوع المصدر',
        default='manual',
        tracking=True,
        help='Source module where this student profile originated from.',
    )
    has_previous_certificate = fields.Boolean(
        string='Has Previous Certificate',
        tracking=True,
    )
    certificate_type = fields.Char(
        string='Previous Certificate Type',
        tracking=True,
    )
    has_issued_certificate = fields.Boolean(
        string='Has Issued Certificate',
        compute='_compute_has_issued_certificate',
        search='_search_has_issued_certificate',
        store=False,
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
        store=True,
        help='Derived from course enrollments (course_detail_ids).',
    )
    current_course_id = fields.Many2one(
        'op.course',
        string='المقرر الحالي',
        compute='_compute_training_summary',
        store=True,
        help='Primary running enrollment: highest ID among running enrollments.',
    )
    current_batch_id = fields.Many2one(
        'op.batch',
        string='الدفعة الحالية',
        compute='_compute_training_summary',
        store=True,
        help='Batch from the primary running enrollment.',
    )
    running_course_count = fields.Integer(
        string='Running Courses',
        compute='_compute_training_summary',
        store=True,
    )
    completed_course_count = fields.Integer(
        string='Completed Courses',
        compute='_compute_training_summary',
        store=True,
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
    has_family_members = fields.Boolean(
        string='Has Family Members',
        compute='_compute_has_family_members',
        help='True when the student has linked parents or siblings.',
    )

    @api.depends('certificate_ids')
    def _compute_certificate_count(self):
        for student in self:
            student.certificate_count = len(student.certificate_ids)

    @api.depends('certificate_ids.state')
    def _compute_has_issued_certificate(self):
        for student in self:
            student.has_issued_certificate = bool(
                student.certificate_ids.filtered(
                    lambda c: c.state in ('issued', 'sent')
                )
            )

    @api.model
    def _search_has_issued_certificate(self, operator, value):
        if operator not in ('=', '!='):
            return []
        issued = self.env['edafaa.student.certificate'].search([
            ('state', 'in', ('issued', 'sent')),
        ]).mapped('student_id').ids
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [('id', 'in', issued or [0])]
        return [('id', 'not in', issued or [0])]

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

    @api.depends('parent_ids', 'parent_ids.student_ids')
    def _compute_has_family_members(self):
        for student in self:
            siblings = student.parent_ids.mapped('student_ids') - student
            student.has_family_members = bool(student.parent_ids or siblings)

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
        students = super().create(vals_list)
        students._sync_partner_profile_fields()
        return students

    def write(self, vals):
        if vals.get('name_english'):
            self._apply_english_name_vals(vals)
        res = super().write(vals)
        sync_fields = {
            'id_number', 'phone', 'street', 'street2', 'city', 'zip',
            'state_id', 'country_id', 'email',
        }
        if sync_fields.intersection(vals):
            self._sync_partner_profile_fields()
        return res

    def _sync_partner_profile_fields(self):
        """Keep res.partner aligned with canonical op.student profile fields."""
        Partner = self.env['res.partner']
        for student in self.filtered('partner_id'):
            partner_vals = {
                'phone': student.phone,
                'street': student.street,
                'street2': student.street2,
                'city': student.city,
                'zip': student.zip,
                'state_id': student.state_id.id if student.state_id else False,
                'country_id': student.country_id.id if student.country_id else False,
                'email': student.email,
            }
            if 'id_number' in Partner._fields:
                partner_vals['id_number'] = student.id_number
            student.partner_id.with_context(
                edafaa_skip_student_sync=True,
            ).write(partner_vals)

    def _apply_english_name_vals(self, vals):
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
        name_english = (name_english or '').strip()
        if not name_english:
            return '', ''
        parts = name_english.split(None, 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        return first_name, last_name

    @api.model
    def _validate_required_profile_vals(self, vals):
        field_checks = [
            ('name_arabic', _('Arabic Name')),
            ('name_english', _('English Name')),
            ('id_number', _('رقم الهوية')),
            ('email', _('Email')),
            ('phone', _('رقم الهاتف')),
            ('street', _('الشارع')),
            ('city', _('المدينة')),
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
            missing.append(_('الدولة'))
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
            ('id_number', _('رقم الهوية')),
            ('email', _('Email')),
            ('phone', _('رقم الهاتف')),
            ('street', _('الشارع')),
            ('city', _('المدينة')),
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
                missing.append(_('الدولة'))
            if missing:
                raise ValidationError(
                    _('Missing required student profile field(s): %s')
                    % ', '.join(missing)
                )
