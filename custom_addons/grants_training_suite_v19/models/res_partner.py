# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime


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

    # Task 2.2.2 - Activity Tracking Fields
    last_activity_date = fields.Datetime(
        string='Last Activity Date',
        compute='_compute_last_activity',
        store=False,
        help='Date of the most recent activity on this contact'
    )

    days_since_activity = fields.Integer(
        string='Days Since Activity',
        compute='_compute_last_activity',
        store=False,
        help='Number of days since the last activity'
    )

    activity_count = fields.Integer(
        string='Activities',
        compute='_compute_activity_count',
        store=False,
        help='Number of activities on this contact'
    )

    def _compute_last_activity(self):
        """Compute last activity date and days since activity"""
        for partner in self:
            # Get most recent activity
            activity = self.env['mail.activity'].search([
                ('res_model', '=', 'res.partner'),
                ('res_id', '=', partner.id)
            ], order='date_deadline desc', limit=1)
            
            if activity:
                partner.last_activity_date = activity.date_deadline
                if activity.date_deadline:
                    delta = datetime.now() - activity.date_deadline
                    partner.days_since_activity = delta.days
                else:
                    partner.days_since_activity = 0
            else:
                partner.last_activity_date = False
                partner.days_since_activity = 0

    def _compute_activity_count(self):
        """Compute total activity count"""
        for partner in self:
            count = self.env['mail.activity'].search_count([
                ('res_model', '=', 'res.partner'),
                ('res_id', '=', partner.id)
            ])
            partner.activity_count = count

    def action_schedule_followup(self):
        """Open activity wizard to schedule a follow-up"""
        self.ensure_one()
        return {
            'name': _('Schedule Activity'),
            'type': 'ir.actions.act_window',
            'res_model': 'mail.activity',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': 'res.partner',
                'default_res_id': self.id,
                'default_activity_type_id': False,
            },
        }

    def action_view_activities(self):
        """Open activities view for this contact"""
        self.ensure_one()
        return {
            'name': _('Activities'),
            'type': 'ir.actions.act_window',
            'res_model': 'mail.activity',
            'view_mode': 'list,form',
            'domain': [
                ('res_model', '=', 'res.partner'),
                ('res_id', '=', self.id)
            ],
            'context': {
                'default_res_model': 'res.partner',
                'default_res_id': self.id,
            },
        }

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

