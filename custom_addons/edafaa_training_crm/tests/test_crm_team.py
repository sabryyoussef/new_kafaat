from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestCrmTeamPipelineTarget(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.team = cls.env['crm.team'].create({
            'name': 'UAT Pipeline Target Team',
            'pipeline_target': 10,
        })

    def test_pipeline_target_field(self):
        self.assertEqual(self.team.pipeline_target, 10)

    def test_update_pipeline_target(self):
        self.team.update_pipeline_target(25)
        self.assertEqual(self.team.pipeline_target, 25)

    def test_opportunity_count_month_counts_pipeline_only(self):
        self.env['crm.lead'].create({
            'name': 'UAT Opportunity 1',
            'type': 'opportunity',
            'team_id': self.team.id,
        })
        self.env['crm.lead'].create({
            'name': 'UAT Lead ignored',
            'type': 'lead',
            'team_id': self.team.id,
        })
        self.team.invalidate_recordset(['opportunity_count_month'])
        self.assertGreaterEqual(self.team.opportunity_count_month, 1)

    def test_leads_do_not_increase_opportunity_count(self):
        before = self.team.opportunity_count_month
        self.env['crm.lead'].create({
            'name': 'UAT Lead only',
            'type': 'lead',
            'team_id': self.team.id,
        })
        self.team.invalidate_recordset(['opportunity_count_month'])
        self.assertEqual(self.team.opportunity_count_month, before)
