# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class SalespersonDashboard(models.TransientModel):
    _name = 'salesperson.dashboard'
    _description = 'Salesperson Dashboard'
    
    def init(self):
        """Log when model is being initialized"""
        _logger.warning('='*80)
        _logger.warning('SALESPERSON DASHBOARD MODEL IS BEING INITIALIZED')
        _logger.warning('Model name: %s', self._name)
        _logger.warning('='*80)
        super(SalespersonDashboard, self).init()

    # KPI Fields
    total_contacts = fields.Integer(
        string='Total Contacts',
        compute='_compute_kpis',
        help='Total number of contacts in assigned pools'
    )

    total_leads = fields.Integer(
        string='Total Leads',
        compute='_compute_kpis',
        help='Total number of leads linked to pool contacts'
    )

    active_leads = fields.Integer(
        string='Active Leads',
        compute='_compute_kpis',
        help='Number of leads in active stages'
    )

    won_leads = fields.Integer(
        string='Won Leads',
        compute='_compute_kpis',
        help='Number of won leads'
    )

    recent_activities = fields.Integer(
        string='Recent Activities',
        compute='_compute_kpis',
        help='Number of activities in the last 7 days'
    )

    idle_contacts = fields.Integer(
        string='Idle Contacts',
        compute='_compute_kpis',
        help='Contacts with no activity in last 30 days'
    )

    def _compute_kpis(self):
        """Compute all KPI values for the logged-in salesperson"""
        for dashboard in self:
            user = self.env.user
            
            # Get pools assigned to this salesperson
            pools = self.env['contact.pool'].search([
                ('sales_person_id', '=', user.id)
            ])
            
            if not pools:
                dashboard.total_contacts = 0
                dashboard.total_leads = 0
                dashboard.active_leads = 0
                dashboard.won_leads = 0
                dashboard.recent_activities = 0
                dashboard.idle_contacts = 0
                continue
            
            # Get all contacts from assigned pools
            contacts = self.env['res.partner'].search([
                ('pool_id', 'in', pools.ids)
            ])
            
            dashboard.total_contacts = len(contacts)
            
            # Get all leads linked to pool contacts
            leads = self.env['crm.lead'].search([
                ('partner_id', 'in', contacts.ids)
            ])
            
            dashboard.total_leads = len(leads)
            
            # Active leads (not won, not lost)
            active_stages = self.env['crm.stage'].search([
                ('is_won', '=', False),
                ('is_lost', '=', False)
            ])
            active_leads = leads.filtered(lambda l: l.stage_id in active_stages)
            dashboard.active_leads = len(active_leads)
            
            # Won leads
            won_leads = leads.filtered(lambda l: l.probability == 100 or getattr(l, 'is_won', False))
            dashboard.won_leads = len(won_leads)
            
            # Recent activities (last 7 days)
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=7)
            recent_activities = self.env['mail.activity'].search_count([
                '|',
                ('res_model', '=', 'res.partner'),
                ('res_model', '=', 'crm.lead'),
                '|',
                ('res_id', 'in', contacts.ids),
                ('res_id', 'in', leads.ids),
                ('date_deadline', '>=', cutoff_date)
            ])
            dashboard.recent_activities = recent_activities
            
            # Idle contacts (no activity in last 30 days)
            idle_cutoff = datetime.now() - timedelta(days=30)
            idle_count = 0
            for contact in contacts:
                has_recent_activity = self.env['mail.activity'].search_count([
                    ('res_model', '=', 'res.partner'),
                    ('res_id', '=', contact.id),
                    ('date_deadline', '>=', idle_cutoff)
                ])
                if not has_recent_activity:
                    idle_count += 1
            dashboard.idle_contacts = idle_count

    def action_view_my_contacts(self):
        """Open my contacts view"""
        user = self.env.user
        pools = self.env['contact.pool'].search([
            ('sales_person_id', '=', user.id)
        ])
        return {
            'name': _('My Contacts'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'list,form,kanban',
            'domain': [('pool_id', 'in', pools.ids)],
            'context': {'search_default_my_contacts': 1},
        }

    def action_view_my_leads(self):
        """Open my leads view"""
        user = self.env.user
        pools = self.env['contact.pool'].search([
            ('sales_person_id', '=', user.id)
        ])
        contacts = self.env['res.partner'].search([
            ('pool_id', 'in', pools.ids)
        ])
        return {
            'name': _('My Leads'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'list,form,kanban',
            'domain': [('partner_id', 'in', contacts.ids)],
            'context': {'search_default_my_leads': 1},
        }

    def action_view_active_leads(self):
        """Open active leads view"""
        user = self.env.user
        pools = self.env['contact.pool'].search([
            ('sales_person_id', '=', user.id)
        ])
        contacts = self.env['res.partner'].search([
            ('pool_id', 'in', pools.ids)
        ])
        active_stages = self.env['crm.stage'].search([
            ('is_won', '=', False),
            ('is_lost', '=', False)
        ])
        return {
            'name': _('Active Leads'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'list,form,kanban',
            'domain': [
                ('partner_id', 'in', contacts.ids),
                ('stage_id', 'in', active_stages.ids)
            ],
            'context': {'search_default_active': 1},
        }

    def action_view_won_leads(self):
        """Open won leads view"""
        user = self.env.user
        pools = self.env['contact.pool'].search([
            ('sales_person_id', '=', user.id)
        ])
        contacts = self.env['res.partner'].search([
            ('pool_id', 'in', pools.ids)
        ])
        return {
            'name': _('Won Leads'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'list,form,kanban',
            'domain': [
                ('partner_id', 'in', contacts.ids),
                ('probability', '=', 100)
            ],
            'context': {'search_default_won': 1},
        }

