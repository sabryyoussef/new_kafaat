# S5 Delivery — OP#358 Batch QR Attendance

**Date:** 2026-07-15  
**Branch:** `feature/meeting-s5-358`  
**Module:** `edafaa_batch_attendance` **`19.0.1.2.0`**  
**DB:** sabry-test (UAT) → TR_K19 (controlled smoke pending)

## Design lock
- Portal check-in (1A), `auth=user`
- Stable QR per batch (regenerate revokes)
- **Option A:** active `op.session` required (no auto-create)
- Late grace **15 minutes from `op.session.start_datetime`**
- Attendance line on session-linked `op.attendance.sheet`
- Error `no_active_session` when no session exists

## Evidence (2026-07-15)
- Unit: `TestMeetingS5BatchQr` **12/12**
- Playwright: `tests/playwright/meeting_s5` **6/6**
- Screenshots under `docs/op_meeting_nabil/evidence/screenshots/` (`s5_358_*`)
- Plan: `docs/op_meeting_nabil/plans/IMPLEMENTATION_PLAN_S5_WP358.md`
- P0: `docs/op_meeting_nabil/analysis/S5_358_P0_FOUNDATION_VALIDATION.md` (Option A locked)

## TR_K19 note
> QR attendance requires staff to schedule/confirm the batch class session before student check-in.  
> Do **not** create sessions automatically on TR_K19.

## Gate
Do **not** close OP#358 / Odoo #49 until TR_K19 controlled smoke + checklist delivery gate complete.
