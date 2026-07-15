# S5 Delivery — OP#358 Batch QR Attendance

**Date:** 2026-07-15  
**Branch:** `feature/meeting-s5-358`  
**Module:** `edafaa_batch_attendance` `19.0.1.0.0`  
**DB:** sabry-test (proof) → TR_K19 (deploy)

## Design lock
- Portal check-in (1A)
- Stable QR per batch (regenerate revokes)
- Late grace 15 minutes

## Evidence
- Unit: `TestMeetingS5BatchQr` 6/6
- Playwright: `tests/playwright/meeting_s5` 3/3
- Screenshots:
  - `docs/op_meeting_nabil/evidence/screenshots/s5_358_batch_form_qr.png`
  - `docs/op_meeting_nabil/evidence/screenshots/s5_358_checkin_success.png`
  - `docs/op_meeting_nabil/evidence/screenshots/s5_358_checkin_rejected.png`

## Acceptance
- Unique stable QR on `op.batch`
- Enrollment (`running`) enforced
- Lines on OpenEduCat today sheet
- Inactive / regenerated token rejected
