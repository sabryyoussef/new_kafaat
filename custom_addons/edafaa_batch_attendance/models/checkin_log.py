from odoo import fields, models


class EdafaaAttendanceCheckinLog(models.Model):
    _name = 'edafaa.attendance.checkin.log'
    _description = 'Batch QR Check-in Log'
    _order = 'create_date desc'

    batch_id = fields.Many2one('op.batch', string='Batch', index=True)
    student_id = fields.Many2one('op.student', string='Student', index=True)
    sheet_id = fields.Many2one('op.attendance.sheet', string='Attendance Sheet')
    line_id = fields.Many2one('op.attendance.line', string='Attendance Line')
    user_id = fields.Many2one('res.users', string='Portal User', index=True)
    ip_address = fields.Char(string='IP Address')
    late = fields.Boolean(string='Late')
    result = fields.Selection(
        selection=[
            ('ok', 'OK'),
            ('already', 'Already checked in'),
            ('rejected_token', 'Invalid token'),
            ('rejected_inactive', 'QR inactive'),
            ('rejected_no_student', 'No student linked'),
            ('rejected_not_enrolled', 'Not enrolled'),
            ('no_active_session', 'No active session'),
            ('rate_limited', 'Rate limited'),
        ],
        string='Result',
        required=True,
        index=True,
    )
    message = fields.Char(string='Message')


class EdafaaAttendanceCheckinAttempt(models.Model):
    _name = 'edafaa.attendance.checkin.attempt'
    _description = 'Batch QR Check-in Attempt (rate limit)'
    _order = 'create_date desc'

    user_id = fields.Many2one('res.users', string='User', index=True)
    ip_address = fields.Char(string='IP Address', index=True)
