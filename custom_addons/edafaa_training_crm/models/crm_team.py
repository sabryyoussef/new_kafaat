from odoo import api, fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    pipeline_target = fields.Integer(
        string='Pipeline Target',
        default=0,
        help='Monthly target number of pipeline opportunities for this sales team.',
    )
    opportunity_count_month = fields.Integer(
        string='Opportunities This Month',
        compute='_compute_opportunity_count_month',
        help='Number of pipeline opportunities created for this team in the current calendar month.',
    )
    pipeline_target_progress = fields.Float(
        string='Pipeline Target Progress (%)',
        compute='_compute_opportunity_count_month',
    )

    @api.depends('pipeline_target')
    def _compute_opportunity_count_month(self):
        today = fields.Date.today()
        month_start = today.replace(day=1)
        Lead = self.env['crm.lead']
        for team in self:
            domain = [
                ('team_id', '=', team.id),
                ('create_date', '>=', fields.Datetime.to_datetime(month_start)),
            ]
            if 'type' in Lead._fields:
                domain.append(('type', '=', 'opportunity'))
            team.opportunity_count_month = Lead.search_count(domain)
            if team.pipeline_target:
                team.pipeline_target_progress = min(
                    100.0,
                    (team.opportunity_count_month / team.pipeline_target) * 100.0,
                )
            else:
                team.pipeline_target_progress = 0.0

    def update_pipeline_target(self, value):
        return self.write({'pipeline_target': int(value or 0)})
