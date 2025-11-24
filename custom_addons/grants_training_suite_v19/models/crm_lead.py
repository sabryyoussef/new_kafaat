# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Task 2.2.3 - Activity Tracking and Pool Fields
    pool_id = fields.Many2one(
        'contact.pool',
        string='Contact Pool',
        related='partner_id.pool_id',
        store=True,
        readonly=True,
        help='Contact pool of the linked partner'
    )

    days_since_activity = fields.Integer(
        string='Days Since Activity',
        compute='_compute_days_since_activity',
        store=False,
        help='Number of days since the last activity on this lead'
    )

    last_activity_date = fields.Datetime(
        string='Last Activity Date',
        compute='_compute_days_since_activity',
        store=False,
        help='Date of the most recent activity on this lead'
    )

    def _compute_days_since_activity(self):
        """Compute days since last activity"""
        for lead in self:
            # Get most recent activity
            activity = self.env['mail.activity'].search([
                ('res_model', '=', 'crm.lead'),
                ('res_id', '=', lead.id)
            ], order='date_deadline desc', limit=1)
            
            if activity and activity.date_deadline:
                lead.last_activity_date = activity.date_deadline
                delta = datetime.now() - activity.date_deadline
                lead.days_since_activity = delta.days
            else:
                lead.last_activity_date = False
                lead.days_since_activity = 0

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-assign user_id based on pool's sales_person_id when lead is created"""
        leads = super(CrmLead, self).create(vals_list)
        
        for lead in leads:
            # Auto-assign user_id if partner has a pool with sales_person_id
            if lead.partner_id and lead.partner_id.pool_id and lead.partner_id.pool_id.sales_person_id:
                if not lead.user_id:
                    lead.user_id = lead.partner_id.pool_id.sales_person_id
                    _logger.info('Auto-assigned lead %s to salesperson %s based on pool', 
                               lead.name, lead.user_id.name)
        
        return leads

    # Task 1.6 - Auto-Move to Won Pool
    def write(self, vals):
        """Override write to auto-move won leads to Pool Won Leads"""
        # Track leads that might become won
        leads_to_check = self
        if 'probability' in vals or 'stage_id' in vals:
            leads_to_check = self
        
        result = super(CrmLead, self).write(vals)

        # Check if any lead became won after the write
        won_leads = leads_to_check.filtered(lambda l: l.probability == 100 or getattr(l, 'is_won', False))
        
        if won_leads:
            won_pool = self.env['contact.pool'].search([
                ('name', '=', 'Pool Won Leads'),
                ('is_system_pool', '=', True)
            ], limit=1)

            if not won_pool:
                # Create Pool Won Leads if it doesn't exist
                won_pool = self.env['contact.pool'].create({
                    'name': 'Pool Won Leads',
                    'is_system_pool': True,
                    'creation_date': fields.Datetime.now(),
                    'created_by': self.env.user.id,
                })

            # Process each won lead
            for lead in won_leads:
                if lead.partner_id:
                    # Remove from old pool if exists
                    old_pool = lead.partner_id.pool_id
                    if old_pool and old_pool != won_pool:
                        # Log in old pool chatter
                        old_pool.message_post(
                            body=_('Contact %s moved to Pool Won Leads (Lead: %s)') % (
                                lead.partner_id.name, lead.name
                            )
                        )

                    # Assign to Pool Won Leads
                    lead.partner_id.pool_id = won_pool

                    # Log in won pool chatter
                    won_pool.message_post(
                        body=_('Contact %s added from won lead: %s') % (
                            lead.partner_id.name, lead.name
                        )
                    )

                    # Log in lead chatter
                    lead.message_post(
                        body=_('Contact moved to Pool Won Leads automatically')
                    )

        return result

