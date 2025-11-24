# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ContactPool(models.Model):
    _name = 'contact.pool'
    _description = 'Contact Pool'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(
        string='Pool Name',
        required=True,
        tracking=True,
        help='Name of the contact pool'
    )

    # Standard audit fields (already inherited from base model)
    # create_date and create_uid are automatically available

    # Task 1.2 - Required Fields
    creation_date = fields.Datetime(
        string='Creation Date',
        default=fields.Datetime.now,
        required=True,
        tracking=True,
        help='Date when the pool was created'
    )

    created_by = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
        help='User who created this pool'
    )

    # Task 1.3 - Contact Relationship (One2many computed from res.partner)
    contact_ids = fields.One2many(
        'res.partner',
        'pool_id',
        string='Contacts',
        help='Contacts assigned to this pool'
    )

    contact_count = fields.Integer(
        string='Contact Count',
        compute='_compute_contact_count',
        store=True,
        help='Number of contacts in this pool'
    )

    # Task 1.4 - Lead Distribution Fields
    sales_person_id = fields.Many2one(
        'res.users',
        string='Sales Person',
        tracking=True,
        help='Sales person assigned to this pool for lead distribution'
    )

    # System fields
    is_system_pool = fields.Boolean(
        string='System Pool',
        default=False,
        help='System-managed pool (cannot be deleted or renamed)'
    )

    # Task 2.2.1 & 2.3.5 - Pool Metrics and Activity Tracking
    last_activity_date = fields.Datetime(
        string='Last Activity Date',
        compute='_compute_pool_activities',
        store=False,
        help='Most recent activity date from contacts in this pool'
    )

    idle_contacts_count = fields.Integer(
        string='Idle Contacts',
        compute='_compute_pool_activities',
        store=False,
        help='Number of contacts with no activity in the last 30 days'
    )

    # Task 2.3.5 - Pool Utilization Metrics
    leads_distributed_count = fields.Integer(
        string='Leads Distributed',
        compute='_compute_pool_metrics',
        store=False,
        help='Total number of leads from contacts in this pool'
    )

    leads_won_count = fields.Integer(
        string='Won Leads',
        compute='_compute_pool_metrics',
        store=False,
        help='Number of won leads from contacts in this pool'
    )

    conversion_rate = fields.Float(
        string='Conversion Rate (%)',
        compute='_compute_pool_metrics',
        store=False,
        digits=(16, 2),
        help='Percentage of leads converted to won'
    )

    average_days_to_convert = fields.Float(
        string='Avg Days to Convert',
        compute='_compute_pool_metrics',
        store=False,
        digits=(16, 1),
        help='Average number of days to convert a lead'
    )

    # Distribution History (stored in chatter via mail.thread)

    @api.depends('contact_ids')
    def _compute_contact_count(self):
        """Compute the number of contacts in the pool"""
        for pool in self:
            pool.contact_count = len(pool.contact_ids)

    @api.depends('contact_ids')
    def _compute_pool_activities(self):
        """Compute activity-related metrics for the pool"""
        for pool in self:
            # Get all contacts in the pool
            contacts = pool.contact_ids
            
            # Get most recent activity date from all contacts
            if contacts:
                activities = self.env['mail.activity'].search([
                    ('res_model', '=', 'res.partner'),
                    ('res_id', 'in', contacts.ids)
                ], order='date_deadline desc', limit=1)
                
                pool.last_activity_date = activities.date_deadline if activities else False
                
                # Count idle contacts (no activity in last 30 days)
                cutoff_date = datetime.now() - timedelta(days=30)
                
                idle_count = 0
                for contact in contacts:
                    contact_activities = self.env['mail.activity'].search([
                        ('res_model', '=', 'res.partner'),
                        ('res_id', '=', contact.id),
                        ('date_deadline', '>=', cutoff_date)
                    ], limit=1)
                    if not contact_activities:
                        idle_count += 1
                
                pool.idle_contacts_count = idle_count
            else:
                pool.last_activity_date = False
                pool.idle_contacts_count = 0

    @api.depends('contact_ids')
    def _compute_pool_metrics(self):
        """Compute pool utilization metrics"""
        for pool in self:
            # Get all contacts in the pool
            contacts = pool.contact_ids
            
            if contacts:
                # Get all leads linked to pool contacts
                leads = self.env['crm.lead'].search([
                    ('partner_id', 'in', contacts.ids)
                ])
                
                pool.leads_distributed_count = len(leads)
                
                # Get won leads
                won_leads = leads.filtered(lambda l: l.probability == 100 or getattr(l, 'is_won', False))
                pool.leads_won_count = len(won_leads)
                
                # Calculate conversion rate
                if pool.leads_distributed_count > 0:
                    pool.conversion_rate = (pool.leads_won_count / pool.leads_distributed_count) * 100
                else:
                    pool.conversion_rate = 0.0
                
                # Calculate average days to convert
                if won_leads:
                    total_days = 0
                    count = 0
                    for lead in won_leads:
                        if lead.create_date:
                            # Use date_closed if available, otherwise use write_date as approximation
                            close_date = getattr(lead, 'date_closed', False) or lead.write_date or datetime.now()
                            if isinstance(close_date, str):
                                close_date = fields.Datetime.from_string(close_date)
                            elif isinstance(close_date, datetime):
                                pass
                            else:
                                close_date = datetime.now()
                            
                            create_dt = lead.create_date
                            if isinstance(create_dt, str):
                                create_dt = fields.Datetime.from_string(create_dt)
                            
                            delta = close_date - create_dt
                            total_days += delta.days
                            count += 1
                    pool.average_days_to_convert = total_days / count if count > 0 else 0.0
                else:
                    pool.average_days_to_convert = 0.0
            else:
                pool.leads_distributed_count = 0
                pool.leads_won_count = 0
                pool.conversion_rate = 0.0
                pool.average_days_to_convert = 0.0

    @api.constrains('name')
    def _check_name(self):
        """Prevent renaming system pools"""
        for pool in self:
            if pool.is_system_pool and pool._origin.name != pool.name:
                raise ValidationError(_('System pools cannot be renamed.'))

    def unlink(self):
        """Prevent deletion of system pools"""
        system_pools = self.filtered('is_system_pool')
        if system_pools:
            raise UserError(_('System pools cannot be deleted.'))
        return super(ContactPool, self).unlink()

    def action_view_contacts(self):
        """Open the contacts in this pool"""
        self.ensure_one()
        return {
            'name': _('Contacts in Pool'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [('pool_id', '=', self.id)],
            'context': {'default_pool_id': self.id},
        }

    def action_distribute_contacts(self):
        """Open the distribution wizard"""
        self.ensure_one()
        return {
            'name': _('Distribute Contacts'),
            'type': 'ir.actions.act_window',
            'res_model': 'contact.pool.distribution.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_pool_id': self.id,
            },
        }

    def action_batch_assign_contacts(self):
        """Open the batch assignment wizard"""
        self.ensure_one()
        return {
            'name': _('Batch Assign Contacts'),
            'type': 'ir.actions.act_window',
            'res_model': 'contact.pool.batch.assignment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_pool_id': self.id,
            },
        }

