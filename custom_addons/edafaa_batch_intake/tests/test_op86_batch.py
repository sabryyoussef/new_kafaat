from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestOp86BatchIntakeProfile(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.department = cls.env['op.department'].create({
            'name': 'OP86 Batch Dept',
            'code': 'OP86-BDEPT',
        })
        cls.program_level = cls.env['op.program.level'].search([], limit=1)
        if not cls.program_level:
            cls.program_level = cls.env['op.program.level'].create({'name': 'OP86 Batch Level'})
        cls.program = cls.env['op.program'].create({
            'name': 'OP86 Test Program',
            'code': 'OP86-PRG',
            'department_id': cls.department.id,
            'program_level_id': cls.program_level.id,
        })

    def test_batch_intake_row_extract(self):
        batch = self.env['batch.intake']
        profile = batch._edafaa_extract_profile_from_row({
            'name': 'CSV User',
            'mobile': '0503333333',
            'address': 'CSV Address',
            'city': 'Jeddah',
            'national_id': '1122334455',
            'program': 'OP86 Test Program',
        })
        self.assertEqual(profile['phone'], '0503333333')
        self.assertEqual(profile['street'], 'CSV Address')
        self.assertEqual(profile['id_number'], '1122334455')
        self.assertEqual(profile['specialization_id'], self.program.id)
