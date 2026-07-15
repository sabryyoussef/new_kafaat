from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, HttpCase


@tagged('post_install', '-at_install')
class TestMeetingS5BatchQr(TransactionCase):
    """S5: OP#358 stable QR + portal check-in into attendance."""

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
        # Edafaa profile required fields when module installed
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
        self.batch.action_generate_qr()
        result = self.service.process_checkin(
            self.batch.attendance_qr_token, self.portal_user,
        )
        self.assertEqual(result['status'], 'ok')
        self.assertTrue(result['line'].present)
        self.assertFalse(result['line'].late)

    def test_already_checked_in(self):
        self.batch.action_generate_qr()
        self.service.process_checkin(self.batch.attendance_qr_token, self.portal_user)
        result = self.service.process_checkin(
            self.batch.attendance_qr_token, self.portal_user,
        )
        self.assertEqual(result['status'], 'already')

    def test_not_enrolled_rejected(self):
        self.batch.action_generate_qr()
        result = self.service.process_checkin(
            self.batch.attendance_qr_token, self.other_user,
        )
        self.assertEqual(result['status'], 'rejected_not_enrolled')

    def test_inactive_and_revoked_token(self):
        self.batch.action_generate_qr()
        old = self.batch.attendance_qr_token
        self.batch.attendance_qr_active = False
        result = self.service.process_checkin(old, self.portal_user)
        self.assertEqual(result['status'], 'rejected_inactive')
        self.batch.attendance_qr_active = True
        self.batch.action_regenerate_qr()
        result = self.service.process_checkin(old, self.portal_user)
        self.assertEqual(result['status'], 'rejected_token')

    def test_late_after_grace(self):
        self.batch.action_generate_qr()
        self.batch.attendance_late_grace_minutes = 15
        sheet = self.service.ensure_today_sheet(self.batch)
        sheet.qr_opened_at = fields.Datetime.now() - timedelta(minutes=20)
        result = self.service.process_checkin(
            self.batch.attendance_qr_token, self.portal_user,
        )
        self.assertEqual(result['status'], 'ok')
        self.assertTrue(result['late'])
        self.assertTrue(result['line'].late)
