from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestMeetingS1StudentProfile(TransactionCase):
    """S1: OP#351 search by id_number + OP#353 voucher_number."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country = cls.env.ref('base.sa')
        cls.department = cls.env['op.department'].create({
            'name': 'S1 Meeting Dept',
            'code': 'S1-MEET-DEPT',
        })
        cls.program_level = cls.env['op.program.level'].search([], limit=1)
        if not cls.program_level:
            cls.program_level = cls.env['op.program.level'].create({'name': 'S1 Level'})
        cls.program = cls.env['op.program'].create({
            'name': 'S1 Meeting Program',
            'code': 'S1-MEET-PRG',
            'department_id': cls.department.id,
            'program_level_id': cls.program_level.id,
        })

    def _student_vals(self, suffix, **extra):
        partner = self.env['res.partner'].create({
            'name': f'S1 Partner {suffix}',
            'email': f's1.{suffix}@test.local',
        })
        vals = {
            'name_arabic': f'S1 Arabic {suffix}',
            'name_english': f'S1 English {suffix}',
            'name': f'S1 English {suffix}',
            'first_name': 'S1',
            'last_name': f'English {suffix}',
            'partner_id': partner.id,
            'email': f's1.{suffix}@test.local',
            'phone': '0501112233',
            'street': 'S1 Street',
            'city': 'Riyadh',
            'country_id': self.country.id,
            'birth_date': '1995-01-01',
            'gender': 'm',
            'id_number': f'1099{suffix}',
            'specialization_id': self.program.id,
        }
        vals.update(extra)
        return vals

    def test_id_number_in_search_view(self):
        view = self.env.ref('edafaa_student_profile.view_op_student_search_edafaa_op86')
        arch = view.arch_db or view.arch
        self.assertIn('id_number', arch)
        self.assertIn('رقم الهوية', arch)

    def test_rec_names_search_includes_id_number(self):
        student = self.env['op.student']
        self.assertIn('id_number', student._rec_names_search)
        self.assertIn('name_arabic', student._rec_names_search)
        self.assertIn('name_english', student._rec_names_search)

    def test_search_and_name_search_by_id_number(self):
        unique_id = '1099555011'
        student = self.env['op.student'].create(self._student_vals(
            's351',
            id_number=unique_id,
        ))
        found = self.env['op.student'].search([('id_number', '=', unique_id)])
        self.assertIn(student, found)
        name_hits = self.env['op.student'].name_search(unique_id, operator='ilike', limit=10)
        hit_ids = [h[0] for h in name_hits]
        self.assertIn(student.id, hit_ids)

    def test_voucher_number_field_and_views(self):
        student = self.env['op.student'].create(self._student_vals(
            's353',
            voucher_number='VCH-S1-001',
        ))
        self.assertEqual(student.voucher_number, 'VCH-S1-001')
        student.write({'voucher_number': 'VCH-S1-002'})
        self.assertEqual(student.voucher_number, 'VCH-S1-002')

        form = self.env.ref('edafaa_student_profile.view_op_student_form_edafaa_profile_inherit')
        form_arch = form.arch_db or form.arch
        self.assertIn('voucher_number', form_arch)

        tree = self.env.ref('edafaa_student_profile.view_op_student_tree_edafaa_op206')
        tree_arch = tree.arch_db or tree.arch
        self.assertIn('voucher_number', tree_arch)

        search = self.env.ref('edafaa_student_profile.view_op_student_search_edafaa_op86')
        search_arch = search.arch_db or search.arch
        self.assertIn('voucher_number', search_arch)

    def test_search_by_voucher_number(self):
        voucher = 'VCH-SEARCH-999'
        student = self.env['op.student'].create(self._student_vals(
            'svch',
            voucher_number=voucher,
        ))
        found = self.env['op.student'].search([('voucher_number', '=', voucher)])
        self.assertIn(student, found)
