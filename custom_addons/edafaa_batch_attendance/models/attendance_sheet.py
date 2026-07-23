from datetime import timedelta

from odoo import _, fields, models
from odoo.exceptions import UserError


class OpAttendanceSheet(models.Model):
    _inherit = 'op.attendance.sheet'

    qr_opened_at = fields.Datetime(
        string='QR Check-in Opened At (legacy audit)',
        help='Deprecated for late policy. Late uses op.session.start_datetime + grace. '
             'Kept for audit of pre-Option-A sheets only; QR path no longer writes this.',
    )


class OpBatchAttendanceMixin(models.AbstractModel):
    """Batch QR portal check-in into OpenEduCat attendance (Option A: requires op.session)."""

    _name = 'edafaa.batch.attendance.service'
    _description = 'Batch QR Attendance Service'

    RATE_LIMIT_PER_MINUTE = 20

    def resolve_student_from_user(self, user):
        """
        Resolve portal user → op.student.

        1. student.user_id
        2. shared partner_id (backfill user_id if empty)
        3. unique email/login match only (backfill if safe)
        4. else empty → rejected_no_student
        """
        Student = self.env['op.student'].sudo()
        student = Student.search([('user_id', '=', user.id)], limit=1)
        if student:
            return student

        if user.partner_id:
            partners = Student.search([('partner_id', '=', user.partner_id.id)])
            if len(partners) == 1:
                student = partners[0]
                if not student.user_id:
                    student.user_id = user.id
                return student
            # Ambiguous partner match — do not backfill

        email = (user.login or user.email or '').strip()
        if email:
            matches = Student.search([('email', '=ilike', email)])
            if len(matches) == 1:
                student = matches[0]
                if not student.user_id:
                    student.user_id = user.id
                return student
            # 0 or >1 — no unsafe backfill
        return Student.browse()

    def student_enrolled_in_batch(self, student, batch):
        return bool(self.env['op.student.course'].sudo().search_count([
            ('student_id', '=', student.id),
            ('batch_id', '=', batch.id),
            ('state', '=', 'running'),
        ]))

    def resolve_active_session(self, batch, now=None):
        """
        Active timetable session for batch at `now`.

        Match: batch_id, course_id, start<=now<=end, active,
        state not cancel. Overlaps: earliest start_datetime wins.
        """
        batch.ensure_one()
        now = now or fields.Datetime.now()
        Session = self.env['op.session'].sudo()
        domain = [
            ('batch_id', '=', batch.id),
            ('course_id', '=', batch.course_id.id),
            ('start_datetime', '<=', now),
            ('end_datetime', '>=', now),
            ('state', 'in', ('draft', 'confirm', 'done')),
            ('active', '=', True),
        ]
        sessions = Session.search(domain, order='start_datetime asc, id asc')
        return sessions[:1]

    def ensure_register(self, batch):
        batch.ensure_one()
        Register = self.env['op.attendance.register'].sudo()
        register = Register.search([
            ('batch_id', '=', batch.id),
            ('course_id', '=', batch.course_id.id),
        ], limit=1)
        if register:
            return register
        code = f'QR{batch.id}'[:16]
        if Register.search([('code', '=', code)], limit=1):
            code = f'Q{batch.id}{fields.Datetime.now().strftime("%H%M%S")}'[:16]
        return Register.create({
            'name': _('QR Attendance — %(batch)s', batch=batch.name)[:64],
            'code': code,
            'course_id': batch.course_id.id,
            'batch_id': batch.id,
        })

    def ensure_session_sheet(self, batch, session):
        """Find/create attendance sheet **always** linked to session_id (Option A)."""
        batch.ensure_one()
        session.ensure_one()
        if not session.id:
            raise UserError(_('Cannot create attendance sheet without an active session.'))

        Sheet = self.env['op.attendance.sheet'].sudo()
        register = self.ensure_register(batch)
        attendance_date = fields.Date.to_date(session.start_datetime)

        # Never use/create session_id=False sheets for QR
        sheet = Sheet.search([
            ('register_id', '=', register.id),
            ('session_id', '=', session.id),
            ('attendance_date', '=', attendance_date),
        ], limit=1)
        vals_extra = {}
        if session.faculty_id:
            vals_extra['faculty_id'] = session.faculty_id.id

        if not sheet:
            sheet = Sheet.create({
                'register_id': register.id,
                'session_id': session.id,
                'attendance_date': attendance_date,
                'state': 'start',
                **vals_extra,
            })
        else:
            if sheet.state in ('draft', 'cancel'):
                sheet.write({'state': 'start'})
            if sheet.state == 'done':
                return sheet
            if vals_extra and not sheet.faculty_id:
                sheet.write(vals_extra)

        if not sheet.session_id:
            raise UserError(_(
                'Internal error: QR attendance sheet missing session_id.'
            ))
        return sheet

    def is_late_for_session(self, session, batch, now=None):
        """Late iff now > session.start_datetime + grace (default 15)."""
        grace = batch.attendance_late_grace_minutes or 15
        now = now or fields.Datetime.now()
        start = fields.Datetime.to_datetime(session.start_datetime)
        limit = start + timedelta(minutes=grace)
        return fields.Datetime.to_datetime(now) > limit

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
            raise UserError(_(
                'Too many check-in attempts. Please wait a minute and try again.'
            ))

    def process_checkin(self, token, user, ip_address=None, now=None):
        """
        Process portal QR check-in against the active batch session.

        Returns dict with status in:
          ok | already | rejected_token | rejected_inactive |
          rejected_no_student | rejected_not_enrolled |
          no_active_session | rate_limited
        """
        Log = self.env['edafaa.attendance.checkin.log'].sudo()
        Batch = self.env['op.batch'].sudo()
        now = now or fields.Datetime.now()

        try:
            self.check_rate_limit(user, ip_address)
        except UserError:
            Log.create({
                'result': 'rate_limited',
                'user_id': user.id,
                'ip_address': ip_address,
                'message': 'Rate limit exceeded',
            })
            return {
                'status': 'rate_limited',
                'message': _('Too many check-in attempts.'),
            }

        batch = Batch.search([('attendance_qr_token', '=', token)], limit=1)
        if not batch:
            Log.create({
                'result': 'rejected_token',
                'user_id': user.id,
                'ip_address': ip_address,
                'message': 'Unknown or revoked token',
            })
            return {
                'status': 'rejected_token',
                'message': _('Invalid or revoked attendance QR.'),
            }

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

        session = self.resolve_active_session(batch, now=now)
        if not session:
            Log.create({
                'result': 'no_active_session',
                'batch_id': batch.id,
                'student_id': student.id,
                'user_id': user.id,
                'ip_address': ip_address,
                'message': 'No overlapping op.session (Option A)',
            })
            return {
                'status': 'no_active_session',
                'batch': batch,
                'student': student,
                'message': _(
                    'No active class session for check-in right now. '
                    'Ask staff to schedule or confirm the class session first.'
                ),
            }

        sheet = self.ensure_session_sheet(batch, session)
        if sheet.state == 'done':
            Log.create({
                'result': 'no_active_session',
                'batch_id': batch.id,
                'student_id': student.id,
                'sheet_id': sheet.id,
                'user_id': user.id,
                'ip_address': ip_address,
                'message': 'Attendance sheet already done',
            })
            return {
                'status': 'no_active_session',
                'batch': batch,
                'student': student,
                'session': session,
                'sheet': sheet,
                'message': _(
                    'Attendance for this session is already closed.'
                ),
            }

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
                'session': session,
                'sheet': sheet,
                'line': line,
                'late': line.late,
                'message': _('You are already checked in for this session.'),
            }

        late = self.is_late_for_session(session, batch, now=now)
        vals = {
            'attendance_id': sheet.id,
            'student_id': student.id,
            'present': True,
            'late': late,
            'absent': False,
            'excused': False,
            'remark': _('QR check-in'),
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
            'session': session,
            'sheet': sheet,
            'line': line,
            'late': late,
            'message': (
                _('Checked in late for %(batch)s.', batch=batch.name)
                if late else
                _('Checked in successfully for %(batch)s.', batch=batch.name)
            ),
        }
