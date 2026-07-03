# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    batch_intake_id = fields.Many2one(
        'batch.intake',
        string='Batch Intake',
        ondelete='set null',
        tracking=True,
        help='Batch intake this student is enrolled in'
    )


class OpStudent(models.Model):
    _inherit = 'op.student'

    batch_intake_id = fields.Many2one(
        'batch.intake',
        string='Batch Intake',
        ondelete='set null',
        tracking=True,
        help='Batch intake this student is enrolled in'
    )

