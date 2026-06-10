from odoo import _, api, fields, models


class OpProgram(models.Model):
    _inherit = 'op.program'

    state = fields.Selection(
        selection=[
            ('draft', 'Draft / مسودة'),
            ('review', 'Under Review / قيد المراجعة'),
            ('approved', 'Approved / معتمد'),
            ('published', 'Published / منشور — متاح للتسجيل'),
            ('archived', 'Archived / أرشيف — غير نشط'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
        copy=False,
    )

    # Phase 4 — enhancement fields
    duration_text = fields.Char(
        string='Program Duration',
        translate=True,
        help='مدة البرنامج — e.g. 40 hours, 2 weeks',
    )
    training_language = fields.Selection(
        selection=[
            ('ar', 'Arabic'),
            ('en', 'English'),
            ('bilingual', 'Bilingual'),
        ],
        string='Training Language',
    )
    max_trainees = fields.Integer(string='Maximum Trainees')
    available_schedules = fields.Text(
        string='Available Schedules',
        translate=True,
    )
    program_objectives = fields.Html(
        string='Program Objectives',
        translate=True,
    )
    career_outcomes = fields.Html(
        string='Career Outcomes',
        translate=True,
    )

    # Phase 3 — tab content fields
    description_html = fields.Html(string='Description', translate=True)
    accreditations_html = fields.Html(string='Accreditations', translate=True)
    target_audience_html = fields.Html(string='Target Audience', translate=True)
    delivery_html = fields.Html(string='Delivery', translate=True)
    pricing_html = fields.Html(string='Pricing', translate=True)
    credentials_html = fields.Html(string='Credentials', translate=True)
    admin_notes = fields.Text(string='Internal Administration Notes')

    # Phase 5 — marketing & course linkage
    brochure = fields.Binary(string='Brochure', attachment=True)
    brochure_filename = fields.Char(string='Brochure Filename')
    marketing_materials = fields.Text(
        string='Marketing Materials',
        translate=True,
    )
    course_ids = fields.One2many(
        'op.course',
        'program_id',
        string='Linked Courses',
    )
    course_count = fields.Integer(
        string='Courses',
        compute='_compute_course_count',
    )

    approved_by_id = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        copy=False,
    )
    approved_date = fields.Datetime(
        string='Approved On',
        readonly=True,
        copy=False,
    )

    @api.depends('course_ids')
    def _compute_course_count(self):
        for program in self:
            program.course_count = len(program.course_ids)

    def action_submit_for_review(self):
        self.write({'state': 'review'})

    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_by_id': self.env.user.id,
            'approved_date': fields.Datetime.now(),
        })

    def action_publish(self):
        self.write({'state': 'published'})

    def action_archive_program(self):
        self.write({'state': 'archived', 'active': False})

    def action_reset_to_draft(self):
        self.write({'state': 'draft', 'active': True})

    def action_view_linked_courses(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Linked Courses'),
            'res_model': 'op.course',
            'view_mode': 'list,form',
            'domain': [('program_id', '=', self.id)],
            'context': {'default_program_id': self.id},
        }
