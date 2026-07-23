# S5 UAT Checklist — OP#358

**Date:** 2026-07-15  
**DB:** sabry-test (UAT) · TR_K19 (controlled smoke)  
**Branch:** `feature/meeting-s5-358`  
**Module:** `edafaa_batch_attendance` `19.0.1.2.0`

## Design lock
- [x] 1A portal (phone)
- [x] Stable QR per batch
- [x] Late = **session.start_datetime + 15 minutes**
- [x] **Option A** — active `op.session` required (no auto session create)

## Batch QR (admin)
- [ ] Generate QR on batch form
- [ ] QR image + URL visible / copyable
- [ ] Regenerate invalidates old token
- [ ] Deactivate rejects check-in
- [ ] Check-in logs open from batch
- [ ] Ops note visible (Option A session requirement)

## UAT session prep (Option A)
- [ ] Controlled `op.session` for QR-target batch (`course_id`, `batch_id`, start/end, non-cancelled)
- [ ] Document for TR_K19: staff must schedule/confirm session before check-in — **no auto session on TR_K19**

## Portal check-in
- [ ] Enrolled + active session within grace → Present
- [ ] After grace → Present + Late
- [ ] Re-scan → Already (one line)
- [ ] No active session → `no_active_session`
- [ ] Non-enrolled → rejected
- [ ] No linked student → rejected
- [ ] Invalid/revoked QR → rejected
- [ ] Arabic UI smoke (`ar_001`)
- [ ] English UI smoke

## Attendance sheet
- [ ] QR path creates/uses sheet with **`session_id` set**
- [ ] QR path does **not** create `session_id=False` sheets
- [ ] Lines match check-ins

## Automated
- [ ] Unit tests green (`/edafaa_batch_attendance`)
- [ ] Playwright `meeting_s5` green

## Delivery gate (do not close until all)
- [ ] Session-based path confirmed
- [ ] Python + Playwright green
- [ ] AR/EN smoke
- [ ] UAT evidence screenshots
- [ ] TR_K19 controlled smoke (with staff session; no auto-create)
- [ ] OP #358 + Odoo #49 comments updated — close only after gate
