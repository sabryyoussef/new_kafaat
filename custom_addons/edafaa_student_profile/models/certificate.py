import base64

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EdafaaStudentCertificate(models.Model):
    _name = 'edafaa.student.certificate'
    _description = 'Student Course Certificate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'issue_date desc, id desc'
    _rec_name = 'certificate_number'

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
    )
    certificate_number = fields.Char(
        string='Certificate Number',
        copy=False,
        readonly=True,
        index=True,
    )
    student_id = fields.Many2one(
        'op.student',
        string='Student',
        required=True,
        ondelete='cascade',
        tracking=True,
    )
    student_course_id = fields.Many2one(
        'op.student.course',
        string='Enrollment',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    course_id = fields.Many2one(
        'op.course',
        string='Course',
        related='student_course_id.course_id',
        store=True,
        readonly=True,
    )
    batch_id = fields.Many2one(
        'op.batch',
        string='Batch',
        related='student_course_id.batch_id',
        store=True,
        readonly=True,
    )
    issue_date = fields.Date(
        string='Issue Date',
        default=fields.Date.context_today,
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('issued', 'Issued'),
            ('sent', 'Sent'),
        ],
        string='Status',
        default='draft',
        tracking=True,
    )
    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Certificate PDF',
        copy=False,
    )
    email_sent = fields.Boolean(
        string='Email Sent',
        default=False,
        copy=False,
    )
    email_sent_date = fields.Datetime(
        string='Email Sent On',
        copy=False,
    )
    notes = fields.Text(string='Notes')

    _unique_student_course = models.Constraint(
        'unique(student_course_id)',
        'A certificate already exists for this enrollment.',
    )
    _unique_certificate_number = models.Constraint(
        'unique(certificate_number)',
        'Certificate number must be unique.',
    )

    @api.depends('certificate_number', 'student_id', 'course_id')
    def _compute_name(self):
        for certificate in self:
            if certificate.certificate_number:
                certificate.name = certificate.certificate_number
            elif certificate.student_id and certificate.course_id:
                certificate.name = '%s — %s' % (
                    certificate.student_id.name_english or certificate.student_id.name,
                    certificate.course_id.name,
                )
            else:
                certificate.name = _('New Certificate')

    @api.constrains('student_course_id')
    def _check_enrollment_finished(self):
        for certificate in self:
            if certificate.state != 'draft':
                continue
            if certificate.student_course_id.state != 'finished':
                raise ValidationError(
                    _('Certificates can only be created for finished enrollments.')
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            enrollment_id = vals.get('student_course_id')
            if enrollment_id:
                enrollment = self.env['op.student.course'].browse(enrollment_id)
                if enrollment.state != 'finished':
                    raise ValidationError(
                        _('Certificates can only be created for finished enrollments.')
                    )
                if vals.get('student_id') and vals['student_id'] != enrollment.student_id.id:
                    raise ValidationError(
                        _('Student does not match the selected enrollment.')
                    )
                vals['student_id'] = enrollment.student_id.id
                if self.search_count([('student_course_id', '=', enrollment_id)]):
                    raise ValidationError(
                        _('A certificate already exists for this enrollment.')
                    )
        return super().create(vals_list)

    def _assign_certificate_number(self):
        self.ensure_one()
        if not self.certificate_number:
            self.certificate_number = (
                self.env['ir.sequence'].next_by_code('edafaa.student.certificate')
            )

    def _generate_pdf_attachment(self):
        self.ensure_one()
        report = self.env.ref(
            'edafaa_student_profile.action_report_student_course_certificate'
        )
        pdf_content, _report_format = report._render_qweb_pdf(
            report.report_name,
            self.ids,
        )
        attachment = self.env['ir.attachment'].create({
            'name': 'Certificate_%s.pdf' % (self.certificate_number or self.id),
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })
        if self.attachment_id:
            self.attachment_id.unlink()
        self.attachment_id = attachment

    def action_issue_certificate(self):
        for certificate in self:
            if certificate.student_course_id.state != 'finished':
                raise ValidationError(
                    _('Certificates can only be issued for finished enrollments.')
                )
            if certificate.state != 'draft':
                raise ValidationError(
                    _('Only draft certificates can be issued.')
                )
            certificate._assign_certificate_number()
            certificate._generate_pdf_attachment()
            certificate.write({
                'state': 'issued',
                'issue_date': fields.Date.context_today(certificate),
            })
        return True

    def action_download_certificate(self):
        self.ensure_one()
        if not self.attachment_id:
            raise ValidationError(_('Certificate PDF has not been generated yet.'))
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % self.attachment_id.id,
            'target': 'new',
        }

    def action_print_certificate(self):
        self.ensure_one()
        if self.state == 'draft':
            raise ValidationError(_('Issue the certificate before printing.'))
        return self.env.ref(
            'edafaa_student_profile.action_report_student_course_certificate'
        ).report_action(self)

    def action_send_certificate_email(self):
        self.ensure_one()
        if self.state not in ('issued', 'sent'):
            raise ValidationError(
                _('Certificate must be issued before sending email.')
            )
        if not self.attachment_id:
            raise ValidationError(_('Certificate PDF has not been generated yet.'))
        student_email = (self.student_id.email or '').strip()
        if not student_email:
            raise ValidationError(
                _('Student email is required to send the certificate.')
            )

        template = self.env.ref(
            'edafaa_student_profile.mail_template_student_course_certificate'
        )
        template.send_mail(
            self.id,
            force_send=True,
            email_values={
                'attachment_ids': [(4, self.attachment_id.id)],
            },
        )

        self.write({
            'state': 'sent',
            'email_sent': True,
            'email_sent_date': fields.Datetime.now(),
        })
        self.message_post(
            body=_('Certificate emailed to %s') % student_email,
            subject=_('Certificate Sent'),
        )
        return True
