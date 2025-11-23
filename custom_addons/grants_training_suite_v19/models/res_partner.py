# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Task 1.3 - Pool Relationship (Option A: Many2one)
    pool_id = fields.Many2one(
        'contact.pool',
        string='Contact Pool',
        tracking=True,
        ondelete='set null',
        help='Contact pool this partner belongs to'
    )

    def action_view_pool_contacts(self):
        """Open the pool and show all contacts in it"""
        self.ensure_one()
        if not self.pool_id:
            return False
        return {
            'name': _('Contacts in Pool'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [('pool_id', '=', self.pool_id.id)],
            'context': {'default_pool_id': self.pool_id.id},
        }

