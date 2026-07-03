from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestEdafaaBatchIntakeBridge(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.department = cls.env['op.department'].create({
            'name': 'Bridge Dept',
            'code': 'BRIDGE-DEPT',
        })
        cls.program_level = cls.env['op.program.level'].search([], limit=1)
        if not cls.program_level:
            cls.program_level = cls.env['op.program.level'].create({'name': 'Bridge Level'})
        cls.program = cls.env['op.program'].create({
            'name': 'Bridge Test Program',
            'code': 'BRIDGE-PRG',
            'department_id': cls.department.id,
            'program_level_id': cls.program_level.id,
        })
        cls.course = cls.env['op.course'].create({
            'name': 'Bridge Test Course',
            'code': 'BRIDGE-CRS',
            'program_id': cls.program.id,
        })
        cls.batch = cls.env['op.batch'].create({
            'name': 'BRIDGE-BATCH',
            'code': 'BRIDGE-BATCH',
            'course_id': cls.course.id,
            'start_date': '2026-01-01',
            'end_date': '2026-12-31',
        })
        cls.intake = cls.env['batch.intake'].create({
            'name': 'Bridge Test Intake',
            'start_date': '2026-01-01',
            'end_date': '2026-12-31',
            'course_id': cls.course.id,
            'state': 'validated',
        })

    def test_process_blocked_without_schedule_batch(self):
        with self.assertRaises(UserError) as ctx:
            self.intake.action_process_file()
        self.assertIn('Schedule Batch is required', str(ctx.exception))

    def _create_test_student(self, partner, email_suffix=''):
        country = self.env.ref('base.sa')
        return self.env['op.student'].create({
            'name': 'Bridge Sync Student',
            'first_name': 'Bridge',
            'last_name': 'Sync',
            'name_arabic': 'طالب تجريبي',
            'name_english': 'Bridge Sync Student',
            'id_number': f'ID-BRIDGE-{email_suffix or "001"}',
            'email': f'bridge.sync.student{email_suffix}@example.com',
            'phone': '+966500000099',
            'street': 'Test Street',
            'city': 'Riyadh',
            'country_id': country.id,
            'birth_date': '2000-01-15',
            'partner_id': partner.id,
            'gender': 'm',
            'batch_intake_id': False,
        })

    def test_partner_sync_on_student_intake_write(self):
        partner = self.env['res.partner'].create({
            'name': 'Bridge Sync Partner',
            'email': 'bridge.sync.partner@example.com',
            'batch_intake_id': False,
        })
        student = self._create_test_student(partner)
        self.assertFalse(partner.batch_intake_id)
        student.write({'batch_intake_id': self.intake.id})
        self.assertEqual(partner.batch_intake_id, self.intake)

    def test_edafaa_batch_intake_menu_exists(self):
        menu = self.env.ref('edafaa_batch_intake.menu_edafaa_batch_intake_list', raise_if_not_found=False)
        self.assertTrue(menu)
        self.assertEqual(menu.parent_id, self.env.ref('openeducat_core.menu_op_general_student'))
