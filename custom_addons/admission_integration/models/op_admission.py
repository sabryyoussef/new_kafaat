# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class OpAdmission(models.Model):
    _inherit = 'op.admission'

    # Source Tracking Fields
    source_type = fields.Selection([
        ('manual', 'Manual Entry'),
        ('student_registration', 'Student Registration Portal'),
        ('batch_intake', 'Batch Intake'),
        ('contact_pool', 'Contact Pool Manager'),
    ], string='Source Type', default='manual', tracking=True,
       help='Source module where this admission originated from')

    source_registration_id = fields.Many2one(
        'student.registration',
        string='Source Registration',
        readonly=True,
        tracking=True,
        help='Student registration record this admission came from'
    )

    source_batch_intake_id = fields.Many2one(
        'batch.intake',
        string='Source Batch Intake',
        readonly=True,
        tracking=True,
        help='Batch intake record this admission came from'
    )

    source_contact_pool_id = fields.Many2one(
        'contact.pool',
        string='Source Contact Pool',
        readonly=True,
        tracking=True,
        help='Contact pool this admission came from'
    )

    source_contact_id = fields.Many2one(
        'res.partner',
        string='Source Contact',
        readonly=True,
        tracking=True,
        help='Contact/Partner record this admission came from'
    )

    is_imported = fields.Boolean(
        string='Imported from External Source',
        default=False,
        tracking=True,
        help='Indicates if this admission was imported from another module'
    )

    def action_open_source_record(self):
        """Open the source record in a new window"""
        self.ensure_one()
        
        if self.source_type == 'student_registration' and self.source_registration_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Source Registration'),
                'res_model': 'student.registration',
                'res_id': self.source_registration_id.id,
                'view_mode': 'form',
                'target': 'new',
            }
        elif self.source_type == 'batch_intake' and self.source_batch_intake_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Source Batch Intake'),
                'res_model': 'batch.intake',
                'res_id': self.source_batch_intake_id.id,
                'view_mode': 'form',
                'target': 'new',
            }
        elif self.source_type == 'contact_pool' and self.source_contact_pool_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Source Contact Pool'),
                'res_model': 'contact.pool',
                'res_id': self.source_contact_pool_id.id,
                'view_mode': 'form',
                'target': 'new',
            }
        else:
            raise UserError(_('No source record found for this admission.'))

