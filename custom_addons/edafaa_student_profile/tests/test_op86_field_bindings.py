from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestOp86FieldBindings(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country = cls.env.ref('base.sa')
        cls.department = cls.env['op.department'].create({
            'name': 'OP86 Dept',
            'code': 'OP86-DEPT',
        })
        cls.program_level = cls.env['op.program.level'].search([], limit=1)
        if not cls.program_level:
            cls.program_level = cls.env['op.program.level'].create({'name': 'OP86 Level'})
        cls.program = cls.env['op.program'].create({
            'name': 'OP86 Test Program',
            'code': 'OP86-PRG',
            'department_id': cls.department.id,
            'program_level_id': cls.program_level.id,
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'OP86 Partner',
            'email': 'op86.partner@test.local',
            'phone': '0500000001',
            'street': 'Test Street',
            'city': 'Riyadh',
            'country_id': cls.country.id,
        })

    def _student_vals(self, suffix):
        return {
            'name_arabic': f'OP86 Arabic {suffix}',
            'name_english': f'OP86 English {suffix}',
            'name': f'OP86 English {suffix}',
            'first_name': 'OP86',
            'last_name': f'English {suffix}',
            'partner_id': self.partner.id,
            'email': f'op86.{suffix}@test.local',
            'phone': '0500000002',
            'street': 'Student Street',
            'city': 'Riyadh',
            'country_id': self.country.id,
            'birth_date': '1995-01-01',
            'gender': 'm',
            'id_number': f'10{suffix}',
            'specialization_id': self.program.id,
        }

    def test_student_syncs_id_and_phone_to_partner(self):
        partner = self.env['res.partner'].create({
            'name': 'Sync Partner',
            'email': 'op86.sync@test.local',
        })
        student = self.env['op.student'].create({
            **self._student_vals('sync'),
            'partner_id': partner.id,
            'email': 'op86.sync.student@test.local',
            'id_number': '1234567890',
            'phone': '0501111111',
        })
        if 'id_number' in partner._fields:
            self.assertEqual(partner.id_number, '1234567890')
        self.assertEqual(partner.phone, '0501111111')

    def test_admission_enroll_maps_id_and_mobile(self):
        register = self.env['op.admission.register'].create({
            'name': 'OP86 Register',
            'start_date': '2026-01-01',
            'end_date': '2026-12-31',
            'min_count': 1,
            'max_count': 100,
        })
        course = self.env['op.course'].create({
            'name': 'OP86 Course',
            'code': 'OP86-CRS',
            'program_id': self.program.id,
        })
        admission = self.env['op.admission'].create({
            'name': 'OP86 Admission',
            'first_name': 'OP86',
            'last_name': 'Admission',
            'email': 'op86.admission@test.local',
            'birth_date': '1995-01-01',
            'course_id': course.id,
            'register_id': register.id,
            'phone': '',
            'mobile': '0502222222',
            'street': 'Adm Street',
            'city': 'Riyadh',
            'country_id': self.country.id,
            'id_number': '9988776655',
            'nationality': self.country.id,
            'specialization_id': self.program.id,
            'state': 'draft',
            'gender': 'm',
        })
        vals = admission.get_student_vals()
        self.assertEqual(vals['phone'], '0502222222')
        self.assertEqual(vals['id_number'], '9988776655')
        self.assertEqual(vals['specialization_id'], self.program.id)

    def test_specialization_stored_on_student(self):
        student = self.env['op.student'].create(self._student_vals('spec'))
        self.assertEqual(student.specialization_id, self.program)
