# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.exceptions import UserError


class BatchIntake(models.Model):
    _inherit = 'batch.intake'

    def action_process_file(self):
        """Require Schedule Batch before processing new intake attempts."""
        self.ensure_one()
        if self.course_id and not self.batch_id:
            raise UserError(_(
                'Schedule Batch is required before processing this intake. '
                'Please select a batch from OpenEduCat Enrollment.'
            ))
        return super().action_process_file()


class OpStudent(models.Model):
    _inherit = 'op.student'

    def write(self, vals):
        """Keep partner batch_intake_id in sync when student intake reference changes."""
        res = super().write(vals)
        if 'batch_intake_id' in vals:
            intake_id = vals['batch_intake_id']
            for student in self:
                partner = student.partner_id
                if not partner:
                    continue
                if partner.batch_intake_id.id != intake_id:
                    partner.write({'batch_intake_id': intake_id})
        return res
