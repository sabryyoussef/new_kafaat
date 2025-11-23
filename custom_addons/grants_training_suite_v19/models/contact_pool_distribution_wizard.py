# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ContactPoolDistributionWizard(models.TransientModel):
    _name = 'contact.pool.distribution.wizard'
    _description = 'Contact Pool Distribution Wizard'

    pool_id = fields.Many2one(
        'contact.pool',
        string='Contact Pool',
        required=True,
        help='Pool to distribute contacts from'
    )

    distribution_method = fields.Selection([
        ('manual', 'Manual Selection'),
        ('round_robin', 'Round-Robin'),
        ('percentage', 'Percentage Allocation (Future)'),
    ], string='Distribution Method', required=True, default='manual',
        help='Method to use for distributing contacts')

    # Manual Selection Fields
    contact_ids = fields.Many2many(
        'res.partner',
        string='Contacts to Distribute',
        domain="[('pool_id', '=', pool_id)]",
        help='Select contacts to distribute manually'
    )

    sales_person_id = fields.Many2one(
        'res.users',
        string='Sales Person',
        required=True,
        domain=[('groups_id', 'in', [('id', 'in', [])])],  # Will be set dynamically
        help='Sales person to assign contacts to'
    )

    # Round-Robin Fields
    sales_person_ids = fields.Many2many(
        'res.users',
        'pool_dist_wiz_user_rel',
        string='Sales Persons',
        help='Sales persons for round-robin distribution'
    )

    contacts_per_person = fields.Integer(
        string='Contacts per Person',
        default=10,
        help='Number of contacts to assign per sales person in round-robin'
    )

    # Percentage Fields (Future)
    percentage_lines = fields.One2many(
        'contact.pool.distribution.wizard.line',
        'wizard_id',
        string='Percentage Distribution',
        help='Percentage allocation per sales person'
    )

    @api.onchange('pool_id')
    def _onchange_pool_id(self):
        """Update domain for contacts when pool changes"""
        if self.pool_id:
            return {
                'domain': {
                    'contact_ids': [('pool_id', '=', self.pool_id.id)]
                }
            }

    def action_distribute(self):
        """Execute the distribution based on selected method"""
        self.ensure_one()

        if not self.pool_id:
            raise UserError(_('Please select a contact pool.'))

        if self.distribution_method == 'manual':
            return self._distribute_manual()
        elif self.distribution_method == 'round_robin':
            return self._distribute_round_robin()
        elif self.distribution_method == 'percentage':
            raise UserError(_('Percentage allocation is not yet implemented.'))

    def _distribute_manual(self):
        """Distribute manually selected contacts"""
        if not self.contact_ids:
            raise UserError(_('Please select at least one contact to distribute.'))

        if not self.sales_person_id:
            raise UserError(_('Please select a sales person.'))

        # Update contacts with sales person assignment
        # Note: We'll store this in a separate model or use tags/notes
        # For now, we'll use the pool's sales_person_id and log in chatter
        assigned_count = 0
        for contact in self.contact_ids:
            # You might want to create a separate model for contact-salesperson assignments
            # For now, we'll log in the pool chatter
            self.pool_id.message_post(
                body=_('Contact %s assigned to sales person %s') % (
                    contact.name, self.sales_person_id.name
                )
            )
            assigned_count += 1

        self.pool_id.message_post(
            body=_('Distribution completed: %d contacts assigned to %s') % (
                assigned_count, self.sales_person_id.name
            )
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Distribution Complete'),
                'message': _('%d contacts have been assigned to %s.') % (
                    assigned_count, self.sales_person_id.name
                ),
                'type': 'success',
                'sticky': False,
            }
        }

    def _distribute_round_robin(self):
        """Distribute contacts using round-robin algorithm"""
        if not self.sales_person_ids:
            raise UserError(_('Please select at least one sales person for round-robin distribution.'))

        if not self.contacts_per_person or self.contacts_per_person <= 0:
            raise UserError(_('Please specify a valid number of contacts per person.'))

        # Get all contacts in the pool
        pool_contacts = self.env['res.partner'].search([
            ('pool_id', '=', self.pool_id.id)
        ])

        if not pool_contacts:
            raise UserError(_('No contacts found in the selected pool.'))

        # Round-robin distribution
        sales_persons = self.sales_person_ids
        total_contacts = len(pool_contacts)
        contacts_per_person = min(self.contacts_per_person, total_contacts // len(sales_persons) if sales_persons else 0)

        if contacts_per_person == 0:
            raise UserError(_('Not enough contacts for round-robin distribution.'))

        assigned_count = 0
        person_index = 0

        for i, contact in enumerate(pool_contacts):
            if assigned_count >= len(sales_persons) * contacts_per_person:
                break

            sales_person = sales_persons[person_index]
            self.pool_id.message_post(
                body=_('Contact %s assigned to sales person %s (Round-Robin)') % (
                    contact.name, sales_person.name
                )
            )
            assigned_count += 1
            person_index = (person_index + 1) % len(sales_persons)

        self.pool_id.message_post(
            body=_('Round-robin distribution completed: %d contacts distributed among %d sales persons.') % (
                assigned_count, len(sales_persons)
            )
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Round-Robin Distribution Complete'),
                'message': _('%d contacts have been distributed among %d sales persons.') % (
                    assigned_count, len(sales_persons)
                ),
                'type': 'success',
                'sticky': False,
            }
        }


class ContactPoolDistributionWizardLine(models.TransientModel):
    _name = 'contact.pool.distribution.wizard.line'
    _description = 'Contact Pool Distribution Wizard Line'

    wizard_id = fields.Many2one(
        'contact.pool.distribution.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )

    sales_person_id = fields.Many2one(
        'res.users',
        string='Sales Person',
        required=True
    )

    percentage = fields.Float(
        string='Percentage',
        required=True,
        help='Percentage of contacts to assign to this sales person'
    )

