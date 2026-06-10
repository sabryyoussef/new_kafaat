from odoo import api, fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    lead_target = fields.Integer(
        string='Lead Target',
        default=0,
        help='Monthly target number of leads for this sales team.',
    )
    lead_count_month = fields.Integer(
        string='Leads This Month',
        compute='_compute_lead_count_month',
        help='Number of leads created for this team in the current calendar month.',
    )
    lead_target_progress = fields.Float(
        string='Lead Target Progress (%)',
        compute='_compute_lead_count_month',
    )

    @api.depends('lead_target')
    def _compute_lead_count_month(self):
        today = fields.Date.today()
        month_start = today.replace(day=1)
        Lead = self.env['crm.lead']
        for team in self:
            domain = [
                ('team_id', '=', team.id),
                ('create_date', '>=', fields.Datetime.to_datetime(month_start)),
            ]
            if 'type' in Lead._fields:
                domain.append(('type', '=', 'lead'))
            team.lead_count_month = Lead.search_count(domain)
            if team.lead_target:
                team.lead_target_progress = min(
                    100.0,
                    (team.lead_count_month / team.lead_target) * 100.0,
                )
            else:
                team.lead_target_progress = 0.0

    def update_lead_target(self, value):
        return self.write({'lead_target': int(value or 0)})
