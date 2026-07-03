from odoo import _, fields, models
from odoo.exceptions import ValidationError


class OpStudentCourse(models.Model):
    _inherit = 'op.student.course'

    certificate_id = fields.Many2one(
        'edafaa.student.certificate',
        string='Certificate',
        compute='_compute_certificate_fields',
        store=False,
    )
    certificate_number = fields.Char(
        string='Certificate No.',
        compute='_compute_certificate_fields',
        store=False,
    )
    certificate_state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('issued', 'Issued'),
            ('sent', 'Sent'),
        ],
        string='Certificate Status',
        compute='_compute_certificate_fields',
        store=False,
    )
    can_issue_certificate = fields.Boolean(
        string='Can Issue Certificate',
        compute='_compute_certificate_fields',
        store=False,
    )

    def _compute_certificate_fields(self):
        Certificate = self.env['edafaa.student.certificate']
        for enrollment in self:
            certificate = Certificate.search(
                [('student_course_id', '=', enrollment.id)],
                limit=1,
            )
            enrollment.certificate_id = certificate
            enrollment.certificate_number = certificate.certificate_number or False
            enrollment.certificate_state = certificate.state if certificate else False
            enrollment.can_issue_certificate = (
                enrollment.state == 'finished' and not certificate
            )

    def action_issue_certificate(self):
        self.ensure_one()
        if self.state != 'finished':
            raise ValidationError(
                _('Certificates can only be issued for finished enrollments.')
            )
        existing = self.env['edafaa.student.certificate'].search(
            [('student_course_id', '=', self.id)],
            limit=1,
        )
        if existing:
            raise ValidationError(
                _('A certificate already exists for this enrollment.')
            )
        certificate = self.env['edafaa.student.certificate'].create({
            'student_id': self.student_id.id,
            'student_course_id': self.id,
        })
        certificate.action_issue_certificate()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Certificate'),
            'res_model': 'edafaa.student.certificate',
            'view_mode': 'form',
            'res_id': certificate.id,
            'target': 'current',
        }

    def action_download_certificate(self):
        self.ensure_one()
        if not self.certificate_id:
            raise ValidationError(_('No certificate exists for this enrollment.'))
        return self.certificate_id.action_download_certificate()

    def action_send_certificate_email(self):
        self.ensure_one()
        if not self.certificate_id:
            raise ValidationError(_('No certificate exists for this enrollment.'))
        return self.certificate_id.action_send_certificate_email()
