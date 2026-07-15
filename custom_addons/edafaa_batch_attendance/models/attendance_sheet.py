from datetime import timedelta

from odoo import _, fields, models
from odoo.exceptions import UserError


class OpAttendanceSheet(models.Model):
    _inherit = 'op.attendance.sheet'

    qr_opened_at = fields.Datetime(
        string='QR Check-in Opened At',
        help='Clock start for late grace when sheet is opened via QR check-in.',
    )


class OpBatchAttendanceMixin(models.AbstractModel):
    """Check-in helpers attached via batch search / controller."""

    _name = 'edafaa.batch.attendance.service'
    _description = 'Batch QR Attendance Service'

    RATE_LIMIT_PER_MINUTE = 20

    def resolve_student_from_user(self, user):
        """Prefer user_id, then partner, then email. Link user_id when found by email."""
        Student = self.env['op.student'].sudo()
        student = Student.search([('user_id', '=', user.id)], limit=1)
        if student:
            return student
        if user.partner_id:
            student = Student.search([('partner_id', '=', user.partner_id.id)], limit=1)
            if student:
                if not student.user_id:
                    student.user_id = user.id
                return student
        email = (user.login or user.email or '').strip()
        if email:
            student = Student.search([('email', '=ilike', email)], limit=1)
            if student:
                if not student.user_id:
                    student.user_id = user.id
                return student
        return Student.browse()

    def student_enrolled_in_batch(self, student, batch):
        return bool(self.env['op.student.course'].sudo().search_count([
            ('student_id', '=', student.id),
            ('batch_id', '=', batch.id),
            ('state', '=', 'running'),
        ]))

    def ensure_today_sheet(self, batch):
        """Find/create attendance register + today's sheet in start state."""
        batch.ensure_one()
        Register = self.env['op.attendance.register'].sudo()
        Sheet = self.env['op.attendance.sheet'].sudo()
        today = fields.Date.context_today(self)

        register = Register.search([
            ('batch_id', '=', batch.id),
            ('course_id', '=', batch.course_id.id),
        ], limit=1)
        if not register:
            code = f'QR{batch.id}'[:16]
            existing = Register.search([('code', '=', code)], limit=1)
            if existing:
                code = f'Q{batch.id}{fields.Datetime.now().strftime("%H%M%S")}'[:16]
            register = Register.create({
                'name': f'QR{batch.id}'[:16],
                'code': code,
                'course_id': batch.course_id.id,
                'batch_id': batch.id,
            })

        sheet = Sheet.search([
            ('register_id', '=', register.id),
            ('attendance_date', '=', today),
            ('session_id', '=', False),
        ], limit=1)
        if not sheet:
            sheet = Sheet.create({
                'register_id': register.id,
                'attendance_date': today,
                'state': 'start',
                'qr_opened_at': fields.Datetime.now(),
            })
        else:
            if sheet.state in ('draft', 'cancel'):
                sheet.write({'state': 'start'})
            if not sheet.qr_opened_at:
                sheet.qr_opened_at = fields.Datetime.now()
        return sheet

    def is_late_for_sheet(self, sheet, batch):
        grace = batch.attendance_late_grace_minutes or 15
        opened = sheet.qr_opened_at or fields.Datetime.now()
        limit = fields.Datetime.to_datetime(opened) + timedelta(minutes=grace)
        return fields.Datetime.now() > limit

    def check_rate_limit(self, user, ip_address):
        Attempt = self.env['edafaa.attendance.checkin.attempt'].sudo()
        since = fields.Datetime.now() - timedelta(minutes=1)
        domain = [('create_date', '>=', fields.Datetime.to_string(since))]
        if user and not user._is_public():
            domain.append(('user_id', '=', user.id))
        elif ip_address:
            domain.append(('ip_address', '=', ip_address))
        else:
            return
        count = Attempt.search_count(domain)
        Attempt.create({
            'user_id': user.id if user and not user._is_public() else False,
            'ip_address': ip_address or False,
        })
        if count >= self.RATE_LIMIT_PER_MINUTE:
            raise UserError(_('Too many check-in attempts. Please wait a minute and try again.'))

    def process_checkin(self, token, user, ip_address=None):
        """
        Process portal QR check-in.

        Returns dict: status in
          ok | already | rejected_token | rejected_inactive |
          rejected_no_student | rejected_not_enrolled | rate_limited
        """
        Log = self.env['edafaa.attendance.checkin.log'].sudo()
        Batch = self.env['op.batch'].sudo()

        try:
            self.check_rate_limit(user, ip_address)
        except UserError:
            Log.create({
                'result': 'rate_limited',
                'user_id': user.id,
                'ip_address': ip_address,
                'message': 'Rate limit exceeded',
            })
            return {'status': 'rate_limited', 'message': _('Too many check-in attempts.')}

        batch = Batch.search([
            ('attendance_qr_token', '=', token),
        ], limit=1)
        if not batch:
            Log.create({
                'result': 'rejected_token',
                'user_id': user.id,
                'ip_address': ip_address,
                'message': 'Unknown or revoked token',
            })
            return {'status': 'rejected_token', 'message': _('Invalid or revoked attendance QR.')}

        if not batch.attendance_qr_active:
            Log.create({
                'result': 'rejected_inactive',
                'batch_id': batch.id,
                'user_id': user.id,
                'ip_address': ip_address,
                'message': 'QR inactive',
            })
            return {
                'status': 'rejected_inactive',
                'batch': batch,
                'message': _('Attendance check-in is disabled for this batch.'),
            }

        student = self.resolve_student_from_user(user)
        if not student:
            Log.create({
                'result': 'rejected_no_student',
                'batch_id': batch.id,
                'user_id': user.id,
                'ip_address': ip_address,
                'message': 'No op.student for user',
            })
            return {
                'status': 'rejected_no_student',
                'batch': batch,
                'message': _('No student profile is linked to your portal account.'),
            }

        if not self.student_enrolled_in_batch(student, batch):
            Log.create({
                'result': 'rejected_not_enrolled',
                'batch_id': batch.id,
                'student_id': student.id,
                'user_id': user.id,
                'ip_address': ip_address,
                'message': 'Not enrolled running',
            })
            return {
                'status': 'rejected_not_enrolled',
                'batch': batch,
                'student': student,
                'message': _('You are not enrolled in this batch.'),
            }

        sheet = self.ensure_today_sheet(batch)
        Line = self.env['op.attendance.line'].sudo()
        line = Line.search([
            ('attendance_id', '=', sheet.id),
            ('student_id', '=', student.id),
        ], limit=1)
        if line and line.present:
            Log.create({
                'result': 'already',
                'batch_id': batch.id,
                'student_id': student.id,
                'sheet_id': sheet.id,
                'line_id': line.id,
                'user_id': user.id,
                'ip_address': ip_address,
                'late': line.late,
                'message': 'Already checked in',
            })
            return {
                'status': 'already',
                'batch': batch,
                'student': student,
                'sheet': sheet,
                'line': line,
                'late': line.late,
                'message': _('You are already checked in for today.'),
            }

        late = self.is_late_for_sheet(sheet, batch)
        vals = {
            'attendance_id': sheet.id,
            'student_id': student.id,
            'present': True,
            'late': late,
            'absent': False,
            'excused': False,
        }
        if line:
            line.write(vals)
        else:
            line = Line.create(vals)

        Log.create({
            'result': 'ok',
            'batch_id': batch.id,
            'student_id': student.id,
            'sheet_id': sheet.id,
            'line_id': line.id,
            'user_id': user.id,
            'ip_address': ip_address,
            'late': late,
            'message': 'Checked in',
        })
        return {
            'status': 'ok',
            'batch': batch,
            'student': student,
            'sheet': sheet,
            'line': line,
            'late': late,
            'message': (
                _('Checked in late for %(batch)s.', batch=batch.name)
                if late else
                _('Checked in successfully for %(batch)s.', batch=batch.name)
            ),
        }
