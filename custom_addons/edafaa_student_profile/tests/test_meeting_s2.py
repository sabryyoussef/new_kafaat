from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestMeetingS2StudentProfile(TransactionCase):
    """S2: OP#352 application_status on op.student (+ portal mapping helper)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country = cls.env.ref('base.sa')
        cls.department = cls.env['op.department'].create({
            'name': 'S2 Meeting Dept',
            'code': 'S2-MEET-DEPT',
        })
        cls.program_level = cls.env['op.program.level'].search([], limit=1)
        if not cls.program_level:
            cls.program_level = cls.env['op.program.level'].create({'name': 'S2 Level'})
        cls.program = cls.env['op.program'].create({
            'name': 'S2 Meeting Program',
            'code': 'S2-MEET-PRG',
            'department_id': cls.department.id,
            'program_level_id': cls.program_level.id,
        })

    def _student_vals(self, suffix, **extra):
        partner = self.env['res.partner'].create({
            'name': f'S2 Partner {suffix}',
            'email': f's2.{suffix}@test.local',
        })
        vals = {
            'name_arabic': f'S2 Arabic {suffix}',
            'name_english': f'S2 English {suffix}',
            'name': f'S2 English {suffix}',
            'first_name': 'S2',
            'last_name': f'English {suffix}',
            'partner_id': partner.id,
            'email': f's2.{suffix}@test.local',
            'phone': '0502223344',
            'street': 'S2 Street',
            'city': 'Riyadh',
            'country_id': self.country.id,
            'birth_date': '1996-02-02',
            'gender': 'm',
            'id_number': f'2099{suffix}',
            'specialization_id': self.program.id,
        }
        vals.update(extra)
        return vals

    def test_default_application_status_under_review(self):
        student = self.env['op.student'].create(self._student_vals('def'))
        self.assertEqual(student.application_status, 'under_review')

    def test_manual_write_all_statuses(self):
        student = self.env['op.student'].create(self._student_vals('manual'))
        for status in ('accepted', 'rejected', 'under_review', 'cancelled'):
            student.write({'application_status': status})
            self.assertEqual(student.application_status, status)
        # ملغي does not archive
        self.assertTrue(student.active)

    def test_application_status_in_views(self):
        form = self.env.ref('edafaa_student_profile.view_op_student_form_edafaa_profile_inherit')
        form_arch = form.arch_db or form.arch
        self.assertIn('application_status', form_arch)
        self.assertIn('حالة الطالب', form_arch)

        tree = self.env.ref('edafaa_student_profile.view_op_student_tree_edafaa_op206')
        tree_arch = tree.arch_db or tree.arch
        self.assertIn('application_status', tree_arch)

        search = self.env.ref('edafaa_student_profile.view_op_student_search_edafaa_op86')
        search_arch = search.arch_db or search.arch
        self.assertIn('application_status', search_arch)
        self.assertIn('group_application_status', search_arch)

    def test_registration_state_mapping_helper(self):
        if 'student.registration' not in self.env:
            self.skipTest('student.registration not installed')
        Reg = self.env['student.registration']
        if not hasattr(Reg, '_map_registration_state_to_application_status'):
            self.skipTest('portal bridge mapping not loaded')
        self.assertEqual(
            Reg._map_registration_state_to_application_status('approved'), 'accepted',
        )
        self.assertEqual(
            Reg._map_registration_state_to_application_status('enrolled'), 'accepted',
        )
        self.assertEqual(
            Reg._map_registration_state_to_application_status('rejected'), 'rejected',
        )
        self.assertEqual(
            Reg._map_registration_state_to_application_status('submitted'), 'under_review',
        )
        self.assertEqual(
            Reg._map_registration_state_to_application_status('draft'), 'under_review',
        )

    def test_search_by_application_status(self):
        accepted = self.env['op.student'].create(self._student_vals(
            'acc', application_status='accepted',
        ))
        rejected = self.env['op.student'].create(self._student_vals(
            'rej', application_status='rejected',
        ))
        found = self.env['op.student'].search([('application_status', '=', 'accepted')])
        self.assertIn(accepted, found)
        self.assertNotIn(rejected, found)
