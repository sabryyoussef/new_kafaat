from odoo import _, api, fields, models
from odoo.exceptions import UserError


class BatchTraineeAssignmentWizard(models.TransientModel):
    _name = 'batch.trainee.assignment.wizard'
    _description = 'Assign Trainees to Batch'

    student_ids = fields.Many2many(
        'op.student',
        string='Trainees',
        required=True,
    )
    course_id = fields.Many2one(
        'op.course',
        string='Course',
        required=True,
    )
    batch_id = fields.Many2one(
        'op.batch',
        string='Batch',
        required=True,
        domain="[('course_id', '=', course_id)]",
    )

    @api.onchange('course_id')
    def _onchange_course_id(self):
        self.batch_id = False

    def action_assign(self):
        self.ensure_one()
        if not self.student_ids:
            raise UserError(_('Select at least one trainee.'))
        assigned = 0
        for student in self.student_ids:
            existing = student.course_detail_ids.filtered(
                lambda line: line.course_id == self.course_id
                and line.batch_id == self.batch_id
            )
            if existing:
                continue
            match = student.course_detail_ids.filtered(
                lambda line: line.course_id == self.course_id and not line.batch_id
            )
            if match:
                match.write({'batch_id': self.batch_id.id})
            else:
                student.write({
                    'course_detail_ids': [(0, 0, {
                        'course_id': self.course_id.id,
                        'batch_id': self.batch_id.id,
                        'state': 'running',
                    })],
                })
            assigned += 1
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Batch Assignment'),
                'message': _('%d trainee(s) assigned to %s.') % (
                    assigned, self.batch_id.display_name,
                ),
                'type': 'success',
                'sticky': False,
            },
        }
