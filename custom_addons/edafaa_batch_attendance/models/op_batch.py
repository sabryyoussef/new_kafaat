import base64
import uuid

from odoo import api, fields, models


class OpBatch(models.Model):
    _inherit = 'op.batch'

    attendance_qr_token = fields.Char(
        string='Attendance QR Token',
        copy=False,
        index=True,
        readonly=True,
    )
    attendance_qr_active = fields.Boolean(
        string='QR Check-in Active',
        default=True,
        help='When disabled, scans of this batch QR are rejected.',
    )
    attendance_qr_url = fields.Char(
        string='Attendance QR URL',
        compute='_compute_attendance_qr',
    )
    attendance_qr_image = fields.Binary(
        string='Attendance QR Image',
        compute='_compute_attendance_qr',
    )
    attendance_late_grace_minutes = fields.Integer(
        string='Late Grace (minutes)',
        default=15,
        help='Check-ins after this many minutes from sheet open are marked late.',
    )

    _attendance_qr_token_unique = models.Constraint(
        'unique(attendance_qr_token)',
        'Attendance QR token must be unique per batch.',
    )

    @api.depends('attendance_qr_token')
    def _compute_attendance_qr(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        Report = self.env['ir.actions.report']
        for batch in self:
            if not batch.attendance_qr_token:
                batch.attendance_qr_url = False
                batch.attendance_qr_image = False
                continue
            url = f'{base_url}/attendance/batch/{batch.attendance_qr_token}'
            batch.attendance_qr_url = url
            try:
                png = Report.barcode('QR', url, width=300, height=300)
                batch.attendance_qr_image = base64.b64encode(png)
            except Exception:
                batch.attendance_qr_image = False

    def action_generate_qr(self):
        for batch in self:
            if not batch.attendance_qr_token:
                batch.attendance_qr_token = uuid.uuid4().hex
                batch.attendance_qr_active = True
        return True

    def action_regenerate_qr(self):
        for batch in self:
            batch.attendance_qr_token = uuid.uuid4().hex
            batch.attendance_qr_active = True
        return True

    def action_toggle_qr_active(self):
        for batch in self:
            batch.attendance_qr_active = not batch.attendance_qr_active
        return True

    def _ensure_qr_token(self):
        self.ensure_one()
        if not self.attendance_qr_token:
            self.action_generate_qr()
        return self.attendance_qr_token
