# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ContactPoolBatchAssignmentWizard(models.TransientModel):
    _name = 'contact.pool.batch.assignment.wizard'
    _description = 'Contact Pool Batch Assignment Wizard'

    pool_id = fields.Many2one(
        'contact.pool',
        string='Contact Pool',
        required=True,
        help='Pool to assign contacts to'
    )

    contact_ids = fields.Many2many(
        'res.partner',
        string='Contacts',
        required=True,
        help='Contacts to assign to the pool'
    )

    remove_from_old_pool = fields.Boolean(
        string='Remove from Old Pool',
        default=True,
        help='If checked, contacts will be removed from their current pool before assignment'
    )

    def action_assign(self):
        """Assign selected contacts to the pool"""
        self.ensure_one()

        if not self.contact_ids:
            raise UserError(_('Please select at least one contact to assign.'))

        if not self.pool_id:
            raise UserError(_('Please select a contact pool.'))

        assigned_count = 0
        moved_count = 0

        for contact in self.contact_ids:
            old_pool = contact.pool_id

            # Remove from old pool if requested
            if self.remove_from_old_pool and old_pool and old_pool != self.pool_id:
                # Log in old pool chatter
                old_pool.message_post(
                    body=_('Contact %s moved to pool: %s') % (
                        contact.name, self.pool_id.name
                    )
                )
                moved_count += 1

            # Assign to new pool
            contact.pool_id = self.pool_id
            assigned_count += 1

        # Log in new pool chatter
        if assigned_count > 0:
            self.pool_id.message_post(
                body=_('Batch assignment: %d contact(s) assigned%s') % (
                    assigned_count,
                    _(' (%d moved from other pools)') % moved_count if moved_count > 0 else ''
                )
            )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Assignment Complete'),
                'message': _('%d contact(s) have been assigned to %s.') % (
                    assigned_count, self.pool_id.name
                ),
                'type': 'success',
                'sticky': False,
            }
        }

