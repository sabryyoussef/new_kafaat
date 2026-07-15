import base64
import io

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

try:
    import openpyxl
except ImportError:  # pragma: no cover
    openpyxl = None


@tagged('post_install', '-at_install')
class TestMeetingS3SalesAssign(TransactionCase):
    """S3: OP#355 Excel assign trainees to sales staff."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if openpyxl is None:
            return
        cls.country = cls.env.ref('base.sa')
        cls.department = cls.env['op.department'].create({
            'name': 'S3 Meeting Dept',
            'code': 'S3-MEET-DEPT',
        })
        cls.program_level = cls.env['op.program.level'].search([], limit=1)
        if not cls.program_level:
            cls.program_level = cls.env['op.program.level'].create({'name': 'S3 Level'})
        cls.program = cls.env['op.program'].create({
            'name': 'S3 Meeting Program',
            'code': 'S3-MEET-PRG',
            'department_id': cls.department.id,
            'program_level_id': cls.program_level.id,
        })
        cls.staff = cls.env['res.users'].create({
            'name': 'S3 Sales Staff',
            'login': 's3.sales.staff',
            'email': 's3.sales@test.local',
            'group_ids': [(6, 0, [cls.env.ref('base.group_user').id])],
        })
        cls.staff2 = cls.env['res.users'].create({
            'name': 'S3 Sales Staff 2',
            'login': 's3.sales.staff2',
            'email': 's3.sales2@test.local',
            'group_ids': [(6, 0, [cls.env.ref('base.group_user').id])],
        })

    def _student(self, suffix, **extra):
        partner = self.env['res.partner'].create({
            'name': f'S3 Partner {suffix}',
            'email': f's3.{suffix}@test.local',
        })
        vals = {
            'name_arabic': f'S3 Arabic {suffix}',
            'name_english': f'S3 English {suffix}',
            'name': f'S3 English {suffix}',
            'first_name': 'S3',
            'last_name': f'English {suffix}',
            'partner_id': partner.id,
            'email': f's3.{suffix}@test.local',
            'phone': '0503334455',
            'street': 'S3 Street',
            'city': 'Riyadh',
            'country_id': self.country.id,
            'birth_date': '1997-03-03',
            'gender': 'm',
            'id_number': f'3099{suffix}',
            'specialization_id': self.program.id,
        }
        vals.update(extra)
        return self.env['op.student'].create(vals)

    def _xlsx_b64(self, rows):
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.append(['id_number', 'staff_login', 'staff_email', 'trainee_name'])
        for row in rows:
            sheet.append(row)
        buf = io.BytesIO()
        wb.save(buf)
        return base64.b64encode(buf.getvalue())

    def test_field_and_views(self):
        self.assertIn('assigned_user_id', self.env['op.student']._fields)
        form = self.env.ref('edafaa_student_profile.view_op_student_form_edafaa_profile_inherit')
        arch = form.arch_db or form.arch
        self.assertIn('assigned_user_id', arch)
        self.assertIn('موظف المبيعات المسؤول', arch)
        search = self.env.ref('edafaa_student_profile.view_op_student_search_edafaa_op86')
        search_arch = search.arch_db or search.arch
        self.assertIn('group_assigned_user', search_arch)

    def test_import_valid_rows(self):
        if openpyxl is None:
            self.skipTest('openpyxl missing')
        s1 = self._student('a001')
        s2 = self._student('a002')
        wizard = self.env['trainee.sales.assign.wizard'].create({
            'filename': 'test.xlsx',
            'data_file': self._xlsx_b64([
                [s1.id_number, self.staff.login, '', s1.name_english],
                [s2.id_number, '', self.staff.email, s2.name_english],
            ]),
        })
        wizard.action_import()
        self.assertEqual(wizard.success_count, 2)
        self.assertEqual(wizard.reject_count, 0)
        self.assertEqual(s1.assigned_user_id, self.staff)
        self.assertEqual(s2.assigned_user_id, self.staff)

    def test_reject_unknown_student_and_staff(self):
        if openpyxl is None:
            self.skipTest('openpyxl missing')
        s1 = self._student('b001')
        wizard = self.env['trainee.sales.assign.wizard'].create({
            'filename': 'test.xlsx',
            'data_file': self._xlsx_b64([
                ['0000000000', self.staff.login, '', 'Missing'],
                [s1.id_number, 'no.such.login', 'no.such@test.local', s1.name_english],
            ]),
        })
        wizard.action_import()
        self.assertEqual(wizard.success_count, 0)
        self.assertEqual(wizard.reject_count, 2)
        self.assertTrue(wizard.reject_file)

    def test_overwrite_assignment(self):
        if openpyxl is None:
            self.skipTest('openpyxl missing')
        s1 = self._student('c001', assigned_user_id=self.staff.id)
        wizard = self.env['trainee.sales.assign.wizard'].create({
            'filename': 'test.xlsx',
            'data_file': self._xlsx_b64([
                [s1.id_number, self.staff2.login, '', s1.name_english],
            ]),
        })
        wizard.action_import()
        self.assertEqual(wizard.success_count, 1)
        self.assertEqual(wizard.overwrite_count, 1)
        self.assertEqual(s1.assigned_user_id, self.staff2)

    def test_empty_file_raises(self):
        if openpyxl is None:
            self.skipTest('openpyxl missing')
        wizard = self.env['trainee.sales.assign.wizard'].create({})
        with self.assertRaises(UserError):
            wizard.action_import()
