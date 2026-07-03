from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestResPartnerStudentBridge(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country = cls.env.ref('base.sa')

    def test_student_created_when_partner_complete(self):
        partner = self.env['res.partner'].create({
            'name': 'UAT Student Contact',
            'is_student': True,
            'email': 'uat.student.bridge.unique@example.com',
            'phone': '+966500000001',
            'street': 'Test Street',
            'city': 'Riyadh',
            'country_id': self.country.id,
            'birth_date': '2000-01-15',
            'id_number': 'ID-UAT-001',
        })
        student = self.env['op.student'].search([
            ('partner_id', '=', partner.id),
        ], limit=1)
        self.assertTrue(student)
        self.assertEqual(student.name_english, 'UAT Student Contact')

    def test_no_student_when_profile_incomplete(self):
        partner = self.env['res.partner'].create({
            'name': 'Incomplete Student',
            'is_student': True,
            'email': 'incomplete@example.com',
        })
        student = self.env['op.student'].search([
            ('partner_id', '=', partner.id),
        ], limit=1)
        self.assertFalse(student)
