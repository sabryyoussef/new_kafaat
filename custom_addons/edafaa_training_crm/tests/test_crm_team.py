from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestCrmTeamLeadTarget(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.team = cls.env['crm.team'].create({
            'name': 'UAT Lead Target Team',
            'lead_target': 10,
        })

    def test_lead_target_field(self):
        self.assertEqual(self.team.lead_target, 10)

    def test_update_lead_target(self):
        self.team.update_lead_target(25)
        self.assertEqual(self.team.lead_target, 25)

    def test_lead_count_month_compute(self):
        self.env['crm.lead'].create({
            'name': 'UAT Lead 1',
            'type': 'lead',
            'team_id': self.team.id,
        })
        self.team.invalidate_recordset(['lead_count_month'])
        self.assertGreaterEqual(self.team.lead_count_month, 1)
