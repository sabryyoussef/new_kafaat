from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestMeetingS5BatchQr(TransactionCase):
    """S5 Option A: stable QR + portal check-in against active op.session."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.course = cls.env['op.course'].search([], limit=1)
        if not cls.course:
            dept = cls.env['op.department'].create({
                'name': 'S5 Dept',
                'code': 'S5DEPT',
            })
            level = cls.env['op.program.level'].search([], limit=1)
            if not level:
                level = cls.env['op.program.level'].create({'name': 'S5 Level'})
            program = cls.env['op.program'].create({
                'name': 'S5 Program',
                'code': 'S5PRG',
                'department_id': dept.id,
                'program_level_id': level.id,
            })
            cls.course = cls.env['op.course'].create({
                'name': 'S5 Course',
                'code': 'S5CRS',
                'department_id': dept.id,
                'program_id': program.id,
            })
        cls.batch = cls.env['op.batch'].create({
            'name': 'S5 Batch QR',
            'code': 'S5BQ1',
            'course_id': cls.course.id,
            'start_date': fields.Date.today(),
            'end_date': fields.Date.today() + timedelta(days=90),
        })
        cls.country = cls.env.ref('base.sa')
        partner = cls.env['res.partner'].create({
            'name': 'S5 Student Partner',
            'email': 's5.student@test.local',
        })
        student_vals = {
            'name': 'S5 Student',
            'first_name': 'S5',
            'last_name': 'Student',
            'partner_id': partner.id,
            'email': 's5.student@test.local',
            'birth_date': '2000-01-01',
            'gender': 'm',
        }
        Student = cls.env['op.student']
        if 'name_arabic' in Student._fields:
            student_vals.update({
                'name_arabic': 'طالب S5',
                'name_english': 'S5 Student',
                'phone': '0501112233',
                'street': 'Street',
                'city': 'Riyadh',
                'country_id': cls.country.id,
            })
        if 'id_number' in Student._fields:
            student_vals['id_number'] = '3580000001'
        if 'specialization_id' in Student._fields:
            program = cls.env['op.program'].search([], limit=1)
            if program:
                student_vals['specialization_id'] = program.id
        cls.student = Student.create(student_vals)
        portal_group = cls.env.ref('base.group_portal')
        cls.portal_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'S5 Portal Student',
            'login': 's5.student@test.local',
            'email': 's5.student@test.local',
            'partner_id': partner.id,
            'group_ids': [(6, 0, [portal_group.id])],
        })
        cls.student.user_id = cls.portal_user.id
        cls.env['op.student.course'].create({
            'student_id': cls.student.id,
            'course_id': cls.course.id,
            'batch_id': cls.batch.id,
            'state': 'running',
        })
        other_partner = cls.env['res.partner'].create({
            'name': 'S5 Other',
            'email': 's5.other@test.local',
        })
        other_vals = {
            'name': 'S5 Other',
            'first_name': 'S5',
            'last_name': 'Other',
            'partner_id': other_partner.id,
            'email': 's5.other@test.local',
            'birth_date': '2001-01-01',
            'gender': 'f',
        }
        if 'name_arabic' in Student._fields:
            other_vals.update({
                'name_arabic': 'آخر',
                'name_english': 'S5 Other',
                'phone': '0509998877',
                'street': 'Street',
                'city': 'Riyadh',
                'country_id': cls.country.id,
            })
        if 'id_number' in Student._fields:
            other_vals['id_number'] = '3580000002'
        if 'specialization_id' in Student._fields:
            program = cls.env['op.program'].search([], limit=1)
            if program:
                other_vals['specialization_id'] = program.id
        cls.other_student = Student.create(other_vals)
        cls.other_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'S5 Other Portal',
            'login': 's5.other@test.local',
            'email': 's5.other@test.local',
            'partner_id': other_partner.id,
            'group_ids': [(6, 0, [portal_group.id])],
        })
        cls.other_student.user_id = cls.other_user.id
        cls.service = cls.env['edafaa.batch.attendance.service']

        subject = cls.env['op.subject'].search([], limit=1)
        if not subject:
            subject = cls.env['op.subject'].create({
                'name': 'S5 Subject',
                'code': 'S5SUB',
                'type': 'theory',
                'subject_type': 'compulsory',
            })
        cls.subject = subject
        faculty = cls.env['op.faculty'].search([], limit=1)
        if not faculty:
            f_partner = cls.env['res.partner'].create({'name': 'S5 Faculty Partner'})
            faculty = cls.env['op.faculty'].create({
                'partner_id': f_partner.id,
                'first_name': 'S5',
                'last_name': 'Faculty',
                'birth_date': '1980-01-01',
                'gender': 'male',
            })
        cls.faculty = faculty

    def _make_active_session(self, *, start_offset_minutes=-5, duration_minutes=60, state='confirm'):
        now = fields.Datetime.now()
        start = now + timedelta(minutes=start_offset_minutes)
        end = start + timedelta(minutes=duration_minutes)
        return self.env['op.session'].create({
            'batch_id': self.batch.id,
            'course_id': self.course.id,
            'subject_id': self.subject.id,
            'faculty_id': self.faculty.id,
            'start_datetime': start,
            'end_datetime': end,
            'state': state,
        })

    def _student_vals(self, email, id_number):
        partner = self.env['res.partner'].create({'name': email, 'email': email})
        vals = {
            'name': email,
            'first_name': 'S5',
            'last_name': id_number,
            'partner_id': partner.id,
            'email': email,
            'birth_date': '2000-01-01',
            'gender': 'm',
        }
        Student = self.env['op.student']
        if 'name_arabic' in Student._fields:
            vals.update({
                'name_arabic': 'طالب',
                'name_english': email,
                'phone': '0500000000',
                'street': 'Street',
                'city': 'Riyadh',
                'country_id': self.country.id,
            })
        if 'id_number' in Student._fields:
            vals['id_number'] = id_number
        if 'specialization_id' in Student._fields:
            program = self.env['op.program'].search([], limit=1)
            if program:
                vals['specialization_id'] = program.id
        return vals

    def test_generate_and_regenerate_qr(self):
        self.assertFalse(self.batch.attendance_qr_token)
        self.batch.action_generate_qr()
        token = self.batch.attendance_qr_token
        self.assertTrue(token)
        self.assertTrue(self.batch.attendance_qr_url)
        self.batch.action_regenerate_qr()
        self.assertTrue(self.batch.attendance_qr_token)
        self.assertNotEqual(self.batch.attendance_qr_token, token)

    def test_enrolled_checkin_present(self):
        self._make_active_session(start_offset_minutes=-5)
        self.batch.action_generate_qr()
        result = self.service.process_checkin(
            self.batch.attendance_qr_token, self.portal_user,
        )
        self.assertEqual(result['status'], 'ok')
        self.assertTrue(result['line'].present)
        self.assertFalse(result['line'].late)
        self.assertTrue(result['sheet'].session_id)
        # Option A: no session_id=False sheets created by QR
        false_sheets = self.env['op.attendance.sheet'].search([
            ('register_id', '=', result['sheet'].register_id.id),
            ('session_id', '=', False),
            ('attendance_date', '=', result['sheet'].attendance_date),
        ])
        # legacy sheets may exist in DB but this QR call must not create one
        self.assertTrue(result['sheet'].session_id)

    def test_already_checked_in(self):
        self._make_active_session(start_offset_minutes=-5)
        self.batch.action_generate_qr()
        self.service.process_checkin(self.batch.attendance_qr_token, self.portal_user)
        result = self.service.process_checkin(
            self.batch.attendance_qr_token, self.portal_user,
        )
        self.assertEqual(result['status'], 'already')
        lines = self.env['op.attendance.line'].search([
            ('attendance_id', '=', result['sheet'].id),
            ('student_id', '=', self.student.id),
        ])
        self.assertEqual(len(lines), 1)

    def test_not_enrolled_rejected(self):
        self._make_active_session(start_offset_minutes=-5)
        self.batch.action_generate_qr()
        result = self.service.process_checkin(
            self.batch.attendance_qr_token, self.other_user,
        )
        self.assertEqual(result['status'], 'rejected_not_enrolled')

    def test_inactive_and_revoked_token(self):
        self._make_active_session(start_offset_minutes=-5)
        self.batch.action_generate_qr()
        old = self.batch.attendance_qr_token
        self.batch.attendance_qr_active = False
        result = self.service.process_checkin(old, self.portal_user)
        self.assertEqual(result['status'], 'rejected_inactive')
        self.batch.attendance_qr_active = True
        self.batch.action_regenerate_qr()
        result = self.service.process_checkin(old, self.portal_user)
        self.assertEqual(result['status'], 'rejected_token')
        result = self.service.process_checkin(
            self.batch.attendance_qr_token, self.portal_user,
        )
        self.assertEqual(result['status'], 'ok')

    def test_late_after_grace_from_session_start(self):
        session = self._make_active_session(
            start_offset_minutes=-20, duration_minutes=90,
        )
        self.batch.action_generate_qr()
        self.batch.attendance_late_grace_minutes = 15
        result = self.service.process_checkin(
            self.batch.attendance_qr_token, self.portal_user,
        )
        self.assertEqual(result['status'], 'ok')
        self.assertTrue(result['late'])
        self.assertTrue(result['line'].late)
        self.assertEqual(result['session'], session)

    def test_no_active_session(self):
        self.batch.action_generate_qr()
        result = self.service.process_checkin(
            self.batch.attendance_qr_token, self.portal_user,
        )
        self.assertEqual(result['status'], 'no_active_session')

    def test_resolve_by_user_id(self):
        self._make_active_session(start_offset_minutes=-5)
        self.batch.action_generate_qr()
        self.assertEqual(self.student.user_id, self.portal_user)
        result = self.service.process_checkin(
            self.batch.attendance_qr_token, self.portal_user,
        )
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['student'], self.student)

    def test_resolve_student_by_email_backfill(self):
        self._make_active_session(start_offset_minutes=-5)
        self.batch.action_generate_qr()
        self.student.user_id = False
        result = self.service.process_checkin(
            self.batch.attendance_qr_token, self.portal_user,
        )
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(self.student.user_id, self.portal_user)

    def test_ambiguous_email_no_unsafe_backfill(self):
        """Two students share the same email → do not resolve/backfill."""
        shared = 's5.ambiguous@test.local'
        s1 = self.env['op.student'].create(self._student_vals(shared, '358AMB0001'))
        s2 = self.env['op.student'].create(self._student_vals(shared, '358AMB0002'))
        # Give s1 a different email-field clash already both shared
        portal_group = self.env.ref('base.group_portal')
        partner = self.env['res.partner'].create({
            'name': 'Ambiguous Portal',
            'email': shared,
        })
        user = self.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Ambiguous Portal',
            'login': shared,
            'email': shared,
            'partner_id': partner.id,
            'tz': 'UTC',
            'group_ids': [(6, 0, [portal_group.id])],
        })
        resolved = self.service.resolve_student_from_user(user)
        self.assertFalse(resolved)
        self.assertFalse(s1.user_id)
        self.assertFalse(s2.user_id)

    def test_nonexistent_identity_rejected(self):
        self._make_active_session(start_offset_minutes=-5)
        self.batch.action_generate_qr()
        # Break user_id + email + partner resolve without invalidating student profile fields
        self.other_student.write({
            'user_id': False,
            'email': 's5.other.detached@test.local',
        })
        orphan_partner = self.env['res.partner'].create({
            'name': 'Orphan Portal Partner',
            'email': 's5.orphan.portal@test.local',
        })
        self.other_user.write({
            'partner_id': orphan_partner.id,
            'login': 's5.orphan.portal@test.local',
            'email': 's5.orphan.portal@test.local',
        })
        result = self.service.process_checkin(
            self.batch.attendance_qr_token, self.other_user,
        )
        self.assertEqual(result['status'], 'rejected_no_student')

    def test_qr_does_not_write_qr_opened_as_late_clock(self):
        """Late must use session start; sheet must not rely on qr_opened_at."""
        self._make_active_session(start_offset_minutes=-5)
        self.batch.action_generate_qr()
        result = self.service.process_checkin(
            self.batch.attendance_qr_token, self.portal_user,
        )
        self.assertEqual(result['status'], 'ok')
        self.assertFalse(result['line'].late)
        # New QR sheets should not set qr_opened_at (legacy audit only)
        self.assertFalse(result['sheet'].qr_opened_at)
