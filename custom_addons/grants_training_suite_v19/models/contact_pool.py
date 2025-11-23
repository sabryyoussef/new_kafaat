# -*- coding: utf-8 -*-

import logging
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

    # Distribution History (stored in chatter via mail.thread)

    @api.depends('contact_ids')
    def _compute_contact_count(self):
        """Compute the number of contacts in the pool"""
        for pool in self:
            pool.contact_count = len(pool.contact_ids)

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

