from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestOp206UatFixes(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country = cls.env.ref('base.sa')
        cls.department = cls.env['op.department'].create({
            'name': 'OP206 Dept',
            'code': 'OP206-DEPT',
        })
        cls.program_level = cls.env['op.program.level'].search([], limit=1)
        if not cls.program_level:
            cls.program_level = cls.env['op.program.level'].create({'name': 'OP206 Level'})
        cls.program = cls.env['op.program'].create({
            'name': 'OP206 Test Program',
            'code': 'OP206-PRG',
            'department_id': cls.department.id,
            'program_level_id': cls.program_level.id,
        })
        cls.course = cls.env['op.course'].create({
            'name': 'OP206 Course',
            'code': 'OP206-CRS',
            'program_id': cls.program.id,
        })

    def _student_vals(self, suffix, **extra):
        partner = self.env['res.partner'].create({
            'name': f'OP206 Partner {suffix}',
            'email': f'op206.{suffix}@test.local',
        })
        vals = {
            'name_arabic': f'OP206 Arabic {suffix}',
            'name_english': f'OP206 English {suffix}',
            'name': f'OP206 English {suffix}',
            'first_name': 'OP206',
            'last_name': f'English {suffix}',
            'partner_id': partner.id,
            'email': f'op206.{suffix}@test.local',
            'phone': '0509990001',
            'street': 'OP206 Street',
            'city': 'Riyadh',
            'country_id': self.country.id,
            'birth_date': '1995-01-01',
            'gender': 'm',
            'id_number': f'20{suffix}',
            'specialization_id': self.program.id,
        }
        vals.update(extra)
        return vals

    def test_current_course_id_is_stored(self):
        field = self.env['op.student']._fields['current_course_id']
        self.assertTrue(field.store)

    def test_group_by_current_course_filter_in_search_view(self):
        view = self.env.ref('edafaa_student_profile.view_op_student_search_edafaa_op86')
        arch = view.arch_db or view.arch
        self.assertIn('group_current_course', arch)
        self.assertIn('current_course_id', arch)

    def test_blood_group_hidden_on_form(self):
        view = self.env.ref('edafaa_student_profile.view_op_student_form_edafaa_profile_inherit')
        arch = view.arch_db or view.arch
        self.assertIn('blood_group', arch)
        self.assertIn('invisible', arch)

    def test_registration_source_fields_on_student(self):
        student = self.env['op.student'].create(self._student_vals(
            'src',
            registration_number='REG00099',
            source_type='student_registration',
        ))
        self.assertEqual(student.registration_number, 'REG00099')
        self.assertEqual(student.source_type, 'student_registration')
        self.assertEqual(student.id_number, '20src')
        self.assertEqual(student.phone, '0509990001')
        self.assertEqual(student.street, 'OP206 Street')
        self.assertEqual(student.specialization_id, self.program)

    def test_admission_maps_source_type(self):
        register = self.env['op.admission.register'].create({
            'name': 'OP206 Register',
            'start_date': '2026-01-01',
            'end_date': '2026-12-31',
            'min_count': 1,
            'max_count': 100,
        })
        admission_vals = {
            'name': 'OP206 Admission',
            'first_name': 'OP206',
            'last_name': 'Admission',
            'email': 'op206.admission@test.local',
            'birth_date': '1995-01-01',
            'course_id': self.course.id,
            'register_id': register.id,
            'phone': '',
            'mobile': '0508887777',
            'street': 'Adm Street',
            'city': 'Riyadh',
            'country_id': self.country.id,
            'id_number': '8877665544',
            'nationality': self.country.id,
            'specialization_id': self.program.id,
            'state': 'draft',
            'gender': 'm',
        }
        if 'source_type' in self.env['op.admission']._fields:
            admission_vals['source_type'] = 'student_registration'
        admission = self.env['op.admission'].create(admission_vals)
        vals = admission.get_student_vals()
        self.assertEqual(vals['phone'], '0508887777')
        self.assertEqual(vals['id_number'], '8877665544')
        self.assertEqual(vals['source_type'], 'student_registration')

    def test_portal_create_maps_registration_number(self):
        Registration = self.env['student.registration']
        if 'specialization_id' not in Registration._fields:
            self.skipTest('portal bridge not installed')
        reg = Registration.create({
            'student_name_english': 'OP206 Portal English',
            'student_name_arabic': 'متدرب بورتال',
            'email': 'op206.portal@test.local',
            'phone': '0507776666',
            'birth_date': '1995-06-01',
            'gender': 'male',
            'nationality': 'Saudi',
            'english_level': 'intermediate',
            'native_language': 'Arabic',
            'requested_courses': 'OP206 Course',
            'street': 'Portal Street',
            'city': 'Riyadh',
            'country_id': self.country.id,
            'id_number': '1122334455',
            'specialization_id': self.program.id,
            'state': 'draft',
        })
        student = reg._create_student_record()
        self.assertEqual(student.registration_number, reg.name)
        self.assertEqual(student.source_type, 'student_registration')
        self.assertEqual(student.id_number, '1122334455')
        self.assertEqual(student.phone, '0507776666')
        self.assertEqual(student.street, 'Portal Street')
        self.assertEqual(student.specialization_id, self.program)
