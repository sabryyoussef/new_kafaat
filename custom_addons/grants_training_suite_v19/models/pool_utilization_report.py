# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class PoolUtilizationReport(models.TransientModel):
    _name = 'pool.utilization.report'
    _description = 'Pool Utilization Report'

    pool_id = fields.Many2one(
        'contact.pool',
        string='Pool',
        help='Select a specific pool or leave empty for all pools'
    )

    date_from = fields.Date(
        string='Date From',
        default=lambda self: fields.Date.context_today(self) - timedelta(days=30),
        required=True,
        help='Start date for the report period'
    )

    date_to = fields.Date(
        string='Date To',
        default=lambda self: fields.Date.context_today(self),
        required=True,
        help='End date for the report period'
    )

    leads_distributed = fields.Integer(
        string='Leads Distributed',
        compute='_compute_metrics',
        help='Total leads created in the period'
    )

    leads_won = fields.Integer(
        string='Leads Won',
        compute='_compute_metrics',
        help='Number of leads won in the period'
    )

    conversion_rate = fields.Float(
        string='Conversion Rate (%)',
        compute='_compute_metrics',
        digits=(16, 2),
        help='Percentage of leads converted'
    )

    idle_leads_count = fields.Integer(
        string='Idle Leads',
        compute='_compute_metrics',
        help='Leads with no activity in last 30 days'
    )

    sales_rep_performance = fields.One2many(
        'pool.sales.rep.performance',
        'report_id',
        string='Sales Rep Performance',
        compute='_compute_metrics',
        help='Performance breakdown by sales rep'
    )

    def _compute_metrics(self):
        """Compute all report metrics"""
        for report in self:
            # Build domain for pools
            pool_domain = []
            if report.pool_id:
                pool_domain = [('id', '=', report.pool_id.id)]
            
            pools = self.env['contact.pool'].search(pool_domain)
            
            if not pools:
                report.leads_distributed = 0
                report.leads_won = 0
                report.conversion_rate = 0.0
                report.idle_leads_count = 0
                report.sales_rep_performance = [(5, 0, 0)]
                continue
            
            # Get all contacts from pools
            contacts = self.env['res.partner'].search([
                ('pool_id', 'in', pools.ids)
            ])
            
            # Get leads in date range
            leads = self.env['crm.lead'].search([
                ('partner_id', 'in', contacts.ids),
                ('create_date', '>=', report.date_from),
                ('create_date', '<=', report.date_to)
            ])
            
            report.leads_distributed = len(leads)
            
            # Won leads
            won_leads = leads.filtered(lambda l: l.probability == 100 or getattr(l, 'is_won', False))
            report.leads_won = len(won_leads)
            
            # Conversion rate
            if report.leads_distributed > 0:
                report.conversion_rate = (report.leads_won / report.leads_distributed) * 100
            else:
                report.conversion_rate = 0.0
            
            # Idle leads (no activity in last 30 days)
            idle_cutoff = datetime.now() - timedelta(days=30)
            idle_count = 0
            for lead in leads:
                has_activity = self.env['mail.activity'].search_count([
                    ('res_model', '=', 'crm.lead'),
                    ('res_id', '=', lead.id),
                    ('date_deadline', '>=', idle_cutoff)
                ])
                if not has_activity:
                    idle_count += 1
            report.idle_leads_count = idle_count
            
            # Sales rep performance
            performance_lines = []
            sales_reps = pools.mapped('sales_person_id').filtered(lambda u: u)
            
            for sales_rep in sales_reps:
                rep_pools = pools.filtered(lambda p: p.sales_person_id == sales_rep)
                rep_contacts = contacts.filtered(lambda c: c.pool_id in rep_pools)
                rep_leads = leads.filtered(lambda l: l.partner_id in rep_contacts)
                rep_won = rep_leads.filtered(lambda l: l.probability == 100 or getattr(l, 'is_won', False))
                
                rep_revenue = sum(rep_won.mapped('expected_revenue')) if hasattr(rep_won, 'expected_revenue') else 0.0
                
                conversion = 0.0
                if len(rep_leads) > 0:
                    conversion = (len(rep_won) / len(rep_leads)) * 100
                
                performance_lines.append((0, 0, {
                    'sales_rep_id': sales_rep.id,
                    'pool_id': rep_pools[0].id if rep_pools else False,
                    'leads_assigned': len(rep_leads),
                    'leads_won': len(rep_won),
                    'conversion_rate': conversion,
                    'total_revenue': rep_revenue,
                }))
            
            report.sales_rep_performance = performance_lines

    def action_view_report(self):
        """Open the report view"""
        self.ensure_one()
        return {
            'name': _('Pool Utilization Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'pool.utilization.report',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }


class PoolSalesRepPerformance(models.TransientModel):
    _name = 'pool.sales.rep.performance'
    _description = 'Sales Rep Performance Line'

    report_id = fields.Many2one(
        'pool.utilization.report',
        string='Report',
        required=True,
        ondelete='cascade'
    )

    sales_rep_id = fields.Many2one(
        'res.users',
        string='Sales Representative',
        required=True
    )

    pool_id = fields.Many2one(
        'contact.pool',
        string='Pool'
    )

    leads_assigned = fields.Integer(
        string='Leads Assigned',
        help='Number of leads assigned to this sales rep'
    )

    leads_won = fields.Integer(
        string='Leads Won',
        help='Number of leads won by this sales rep'
    )

    conversion_rate = fields.Float(
        string='Conversion Rate (%)',
        digits=(16, 2),
        help='Conversion rate for this sales rep'
    )

    total_revenue = fields.Monetary(
        string='Total Revenue',
        currency_field='currency_id',
        help='Total revenue from won leads'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

