from odoo import http
from odoo.http import request


class AttendanceQrController(http.Controller):

    @http.route(
        '/attendance/batch/<string:token>',
        type='http',
        auth='user',
        website=True,
        methods=['GET', 'POST'],
        csrf=False,
    )
    def batch_checkin(self, token, **kw):
        """
        Portal QR check-in.

        auth='user' forces login; Odoo preserves return via redirect=/attendance/batch/<token>.
        """
        service = request.env['edafaa.batch.attendance.service']
        ip = request.httprequest.environ.get('REMOTE_ADDR')
        result = service.process_checkin(token, request.env.user, ip_address=ip)
        status = result.get('status')
        template = {
            'ok': 'edafaa_batch_attendance.checkin_success',
            'already': 'edafaa_batch_attendance.checkin_already',
            'rejected_token': 'edafaa_batch_attendance.checkin_rejected',
            'rejected_inactive': 'edafaa_batch_attendance.checkin_rejected',
            'rejected_no_student': 'edafaa_batch_attendance.checkin_rejected',
            'rejected_not_enrolled': 'edafaa_batch_attendance.checkin_rejected',
            'no_active_session': 'edafaa_batch_attendance.checkin_rejected',
            'rate_limited': 'edafaa_batch_attendance.checkin_rejected',
        }.get(status, 'edafaa_batch_attendance.checkin_rejected')
        lang = (request.env.lang or '').startswith('ar')
        return request.render(template, {
            'status': status,
            'message': result.get('message'),
            'batch': result.get('batch'),
            'student': result.get('student'),
            'session': result.get('session'),
            'late': result.get('late'),
            'is_rtl': lang,
        })
