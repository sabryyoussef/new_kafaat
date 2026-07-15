import logging

from odoo import models

_logger = logging.getLogger(__name__)


class StudentRegistration(models.Model):
    _inherit = 'student.registration'

    def action_final_approve(self):
        res = super().action_final_approve()
        for record in self:
            student = record.student_id
            if not student or student._name != 'op.student':
                continue
            # Link portal user created for this email
            user = self.env['res.users'].sudo().search(
                [('login', '=', record.email)], limit=1,
            )
            if user and not student.user_id:
                student.sudo().write({'user_id': user.id})
                _logger.info(
                    'Linked portal user %s to op.student %s after finalize',
                    user.id, student.id,
                )
            elif user and student.user_id and student.user_id.id != user.id:
                _logger.warning(
                    'op.student %s already has user_id %s; finalize user is %s',
                    student.id, student.user_id.id, user.id,
                )
        return res
