# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

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

