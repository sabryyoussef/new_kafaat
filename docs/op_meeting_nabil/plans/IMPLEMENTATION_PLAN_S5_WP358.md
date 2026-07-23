# S5 Implementation Plan — Batch QR Attendance (OP#358 / Odoo #49)

**Status:** Implementation-ready (design locked)  
**Sprint:** S5  
**OpenProject:** [#358](https://master.tailcf9988.ts.net:10081/work_packages/358) — *[Kafaat] Batch attendance with QR code per batch*  
**Odoo task:** [#49](http://127.0.0.1:8069/web#id=49&model=project.task&view_type=form&db=sabry-test)  
**Parent:** OP#87 `edafa_kafaat_parent`  
**Module:** `edafaa_batch_attendance`  
**Branch:** `feature/meeting-s5-358`  
**Runtime path:** `/opt/localaddons/edafaa_batch_attendance/`  
**Repo mirror:** `/opt/new_kafaat/custom_addons/edafaa_batch_attendance/`  
**Depends on:** `openeducat_attendance`, `openeducat_core`, `openeducat_timetable` (session clock), `portal`, `website`, `student_enrollment_portal`

---

## Design locks (do not reopen in S5)

| Topic | Locked choice |
|-------|----------------|
| Check-in UX | **1A — Student Portal (phone)**. Student must be logged in; scan opens portal browser route; attendance uses OpenEduCat foundation. |
| QR lifetime | **Stable per Batch** for the batch period. Regenerate/revoke if compromised. **No** daily / per-session QR regeneration. |
| Late policy | Allow check-in after session start. Grace **15 minutes** from **session start**. ≤15 min → Present (not late). &gt;15 min → Present + Late. |
| Duplicate | Prevent duplicate check-in for same student / same attendance sheet (session). |
| Scope | Batch QR attendance only. No biometric, GPS/geofence, NFC, rotating QR, kiosk. |
| Data | Reuse `op.attendance.register` / `sheet` / `line`. Do not invent a parallel attendance ledger. Keep course/batch/student selection keys stable. |

If a lock is blocked by missing data (e.g. no timetable sessions for a batch), document the gap, implement the **minimum** remediation inside S5, and do **not** silently replace the lock with another UX.

---

## Goal

Let enrolled students check attendance by scanning a **stable batch QR** on their phone while logged into the student portal, writing **Present / Late** lines into existing OpenEduCat attendance models for the **active batch session**.

---

## 1. Current-state analysis

### 1.1 Attendance foundation (`openeducat_attendance`)

| Model | Path | Role for S5 |
|-------|------|-------------|
| `op.attendance.register` | `.../models/attendance_register.py` | Per course + **required** `batch_id` (+ optional subject). |
| `op.attendance.sheet` | `.../models/attendance_sheet.py` | Daily/session sheet: `register_id`, optional `session_id` → `op.session`, `attendance_date`, `state` (`draft`/`start`/`done`/`cancel`), O2M lines. Unique `(register_id, session_id, attendance_date)`. |
| `op.attendance.line` | `.../models/attendance_line.py` | `student_id`, booleans `present` / `late` / `excused` / `absent`. Unique `(student_id, attendance_id, attendance_date)`. |
| `op.session` bridge | `.../models/attendance_session.py` | `op.session.get_attendance()` opens/creates sheet linked to session. |

Staff API `/openeducat-attendance/take-attendance` marks remaining enrolled students present — **not** a student self-check-in path. Reuse models only; do not extend that API for S5.

### 1.2 Batch / enrollment / session

| Concept | Source |
|---------|--------|
| `op.batch` | `openeducat_core` — `course_id`, `start_date`, `end_date` |
| Enrollment | `op.student.course` — `student_id`, `course_id`, `batch_id`, `state` (`running`/`finished`) |
| Timetable session | `op.session` (`openeducat_timetable`) — `course_id`, `batch_id`, `start_datetime`, `end_datetime`, `state` |

**QR gate:** student must have `op.student.course` with matching `batch_id` and `state='running'`.

### 1.3 Portal authentication and student ↔ user linkage

| Layer | Behavior | Reliability |
|-------|----------|-------------|
| `op.student.user_id` | Optional **stored** Many2one → `res.users` (`create_student_user()` sets it). | Correct when set; often empty for legacy / portal-enrollment students. |
| `op.student.partner_id` | Required `_inherits` partner. | Stable identity; portal user may **not** share this partner. |
| Enrollment portal finalize | `student_enrollment_portal`: creates student then portal user; base path can create a **separate** partner for the user and **does not** set `student.user_id`. | **Known gap.** |

**Minimum S5 fix (required):**

1. Resolver order: `user_id` → `partner_id` → email/`login` (`=ilike`); when found via partner/email, **backfill** `student.user_id`.
2. On registration final approve (inherit): if student exists and portal user matches email/login and `user_id` empty → set `user_id`.

Without (1)+(2), many real portal students hit `rejected_no_student`.

### 1.4 Scaffold already present (align, do not fork)

Module `edafaa_batch_attendance` already contains token fields, portal route, service, logs, unit tests, and admin QR UI. Treat it as the implementation base.

**Aligned with locks today:** portal `auth=user`, stable token, regenerate, enrollment check, OpenEduCat lines, duplicate “already”, revoke/inactive, rate limit, linkage resolver + finalize backfill.

**Must realign to locks (current drift):**

| Topic | Current scaffold | Locked S5 behavior |
|-------|------------------|--------------------|
| Active container | Today’s sheet with `session_id=False` | Sheet linked to **active `op.session`** for the batch |
| Late clock | `sheet.qr_opened_at` (first QR open) | **`op.session.start_datetime` + 15 minutes** |
| No session | Implicitly creates a day sheet | Explicit error **`no_active_session`** (unless minimum remediation approved — see §5 / §16) |

Do **not** keep day-only sheets as the primary path when implementing this plan.

### 1.5 Related docs

| Doc | Path |
|-----|------|
| Short prior plan | `plans/PLAN_WP358.md` (superseded by **this** document) |
| Analysis (stale status) | `analysis/WP358_batch_qr_attendance.md` |
| UAT checklist | `plans/S5_UAT_CHECKLIST.md` |
| Delivery note | `evidence/S5_358_DELIVERY_NOTE.md` |

---

## 2. Proposed data model changes

### 2.1 Extend `op.batch` (QR identity)

| Field | Type | Notes |
|-------|------|-------|
| `attendance_qr_token` | `Char`, indexed, `copy=False`, readonly | Opaque random hex/uuid. Unique constraint. |
| `attendance_qr_active` | `Boolean`, default `True` | Soft revoke without rotating token. |
| `attendance_qr_url` | Computed `Char` | `{web.base.url}/attendance/batch/{token}` |
| `attendance_qr_image` | Computed `Binary` | PNG via `ir.actions.report.barcode('QR', url, …)` |
| `attendance_late_grace_minutes` | `Integer`, default **15** | Keep field for ops visibility; S5 policy fixed at 15 unless product later unlocks. |

**Actions (admin):**

- `action_generate_qr` — mint token if missing; set active.
- `action_regenerate_qr` — new token (old URL dies); set active. Persist previous token optionally in audit only — not required for S5.
- `action_toggle_qr_active` — disable/enable without regenerating.

**Do not** stamp daily tokens or session ids into the QR URL.

### 2.2 Reuse attendance sheet/line (no parallel ledger)

- Prefer sheet with `session_id` = resolved active session, `register_id` for batch+course, `state='start'` during check-in window.
- Lines: `present=True`, `late` per §6, clear `absent`/`excused` on successful scan.
- Unique constraint on line already enforces one row per student/sheet/date.

### 2.3 Optional sheet helper

- Prefer late clock from `session_id.start_datetime` only.
- Keep `qr_opened_at` **only** if still useful for audit; **do not** use it for Present/Late once session lock is implemented. Remove or stop reading it in `is_late_*` logic.

### 2.4 Audit models (recommended, already sketched)

| Model | Purpose |
|-------|---------|
| `edafaa.attendance.checkin.log` | Outcome per attempt: ok / already / rejected_* / rate_limited; student, batch, sheet, line, late, user, IP, message. |
| `edafaa.attendance.checkin.attempt` | Soft rate-limit counter (e.g. 20/min/user or IP). |

Access: internal users (attendance / education managers); no portal create rights beyond controller `sudo` path.

### 2.5 Enrollment linkage fix

Inherit enrollment final approve (module already depends on `student_enrollment_portal`) to set `op.student.user_id` when portal user login matches student email — see §4.

---

## 3. Portal QR check-in route and security flow

### 3.1 Route

```text
GET|POST /attendance/batch/<string:token>
  auth='user'
  website=True
```

- Unauthenticated → Odoo login / portal login redirect, then return to same URL.
- Prefer `csrf=True` for POST if POST is used; if single GET performs check-in (current), document CSRF trade-off and keep rate limits + auth floor (§11).

### 3.2 Flow (happy path)

```
Scan QR
  → open /attendance/batch/<token>
  → require logged-in portal user
  → resolve token → op.batch (must exist, attendance_qr_active)
  → resolve user → op.student (§4)
  → assert running enrollment on that batch
  → resolve active op.session for batch (§5)
  → ensure register + sheet for that session (§5)
  → upsert line Present/Late (§6–7)
  → write check-in log
  → render portal success/already/rejected template (AR/EN)
```

### 3.3 Security floor

- `auth='user'` — anonymous scans cannot create attendance.
- Token entropy: `uuid4().hex` (or equivalent).
- Lookup by exact token; regenerated token invalidates prior URL.
- Inactive flag rejects without revealing enrollment details beyond generic message where possible.
- Rate limit failed/spam attempts.

---

## 4. Resolve logged-in portal user → `op.student`

Implement on service model (e.g. `edafaa.batch.attendance.service`):

```text
1. search op.student where user_id = user.id
2. else search where partner_id = user.partner_id.id  → backfill user_id
3. else search where email =ilike (user.login or user.email) → backfill user_id
4. else → rejected_no_student
```

**Finalize hook:** after successful student + portal user creation on registration approve, set `student.user_id` when email/login matches.

**Ops note for TR_K19:** one-time SQL/ORM script optional to backfill `user_id` for existing students where email matches portal login — include in deployment if UAT shows widespread `rejected_no_student`.

---

## 5. Determine active attendance session for the student's batch

Locked design requires attendance against the **correct session**, and late relative to **session start**.

### 5.1 Resolution algorithm (canonical)

Given `batch` and `now = fields.Datetime.now()` (user TZ via context when needed):

1. Search `op.session` where:
   - `batch_id = batch.id`
   - `course_id = batch.course_id.id` (defense in depth)
   - `start_datetime <= now <= end_datetime`
   - exclude cancelled / closed states if used in this DB (inspect live selection values on `op.session.state`)
2. If multiple overlaps → pick nearest `start_datetime` (or earliest start); log ambiguity.
3. If none in window → **optional short lookback** only if product confirms (default for S5: **none**). Prefer hard fail `no_active_session`.
4. Ensure `op.attendance.register` for `(course_id, batch_id)` (create if missing, stable code `QR{batch_id}` style).
5. Find sheet: `(register_id, session_id, attendance_date=session.start_datetime.date())`.
6. If missing → create with `state='start'`, `session_id` set, `faculty_id` from session if available.
7. If sheet `draft`/`cancel` → move to `start` for QR window (do not silently reopen `done` unless UAT asks — default: allow check-in on `start` and `draft`→`start`; reject or read-only message if `done`/`cancel`).

### 5.2 Sheet uniqueness

Respect `unique(register_id, session_id, attendance_date)`. Never invent a second sheet for the same session/date.

### 5.3 Session foundation remediation — **LOCKED: Option A**

P0 found insufficient session coverage on sabry-test / TR_K19. Product lock (2026-07-15):

> **Option A — Operational Session Requirement:** staff must create/confirm an `op.session` covering check-in time. S5 does **not** auto-create sessions.

- QR returns `no_active_session` when no overlapping session exists.
- Do **not** implement Option B (session helper) in S5.
- Do **not** fall back to `session_id=False` / `qr_opened_at`.
- TR_K19: document that staff schedule/confirm the class session before students scan; create **no** sessions automatically on TR_K19.

See [S5_358_P0_FOUNDATION_VALIDATION.md](../analysis/S5_358_P0_FOUNDATION_VALIDATION.md).

---

## 6. Present / Late calculation (15-minute grace)

```text
grace = batch.attendance_late_grace_minutes or 15   # locked default 15
start = session.start_datetime
if now <= start + grace:
    present=True, late=False
else:
    present=True, late=True
```

- Check-in **before** `start_datetime`: product default for S5 = **allow** as Present not late (early), unless UAT forbids — document choice in tests as early=present.
- Check-in **after** `end_datetime`: treat as `no_active_session` (session resolution failed) — do not write lines on expired sessions.
- Never flip a prior successful Present→Late on re-scan (idempotent — §7).

---

## 7. Duplicate check-in prevention and idempotency

1. Search `op.attendance.line` for `(attendance_id=sheet, student_id=student)`.
2. If exists and `present=True` → return status `already` (same messages, show prior late flag). **Do not** update timestamps in a way that changes late.
3. If exists but not present (staff marked absent) → S5 default: upgrade to present/late from QR (document); alternatively reject — prefer upgrade with audit remark `QR check-in`.
4. Rely on SQL unique constraint as last resort; catch and map to `already`.
5. Always append check-in log for both `ok` and `already`.

Idempotency key: `(student_id, sheet_id)` for the resolved session sheet.

---

## 8. Error states

| Status code | Condition | Portal message (EN intent) | Arabic intent |
|-------------|-----------|----------------------------|---------------|
| `rejected_token` | Unknown token (never minted / regenerated) | Invalid or revoked attendance QR. | رمز الحضور غير صالح أو مُلغى. |
| `rejected_inactive` | `attendance_qr_active=False` | Check-in disabled for this batch. | تسجيل الحضور متوقف لهذه الدفعة. |
| `rejected_no_student` | No `op.student` for portal user | No student profile linked to your account. | لا يوجد ملف متدرب مرتبط بحسابك. |
| `rejected_not_enrolled` | No running `op.student.course` for QR batch | You are not enrolled in this batch. | لست مسجلاً في هذه الدفعة. |
| `no_active_session` | No overlapping `op.session` (or sheet refused) | No active class session for check-in now. | لا توجد حصة نشطة لتسجيل الحضور الآن. |
| `already` | Line already present | Already checked in for this session. | تم تسجيل حضورك مسبقاً لهذه الحصة. |
| `ok` | New/updated present line | Checked in successfully / Checked in late. | تم تسجيل الحضور / تم التسجيل مع تأخير. |
| `rate_limited` | Too many attempts | Too many attempts; try again shortly. | محاولات كثيرة؛ حاول بعد قليل. |

All rejections go to the rejected template with the specific message; log `result` precisely for support.

---

## 9. Backend UI (administrators)

On `op.batch` form, notebook page **Attendance QR**:

- Fields: active toggle, grace minutes (readonly 15 if policy hardcoded in UI help), URL (copy), QR image.
- Buttons: Generate / Regenerate (confirm wizard: “Old QR stops working”) / Toggle active.
- Download: save QR image (browser download of binary) and/or print report `report_batch_attendance_qr` (optional A4 with batch name + URL).
- Smart button / menu: Check-in logs filtered by `batch_id`.
- Groups: Education Manager / Attendance / Settings — mirror OpenEduCat attendance rights; students never see token fields.

Do not change batch selection keys or enrollment wizards beyond linkage backfill.

---

## 10. Portal UX and AR/EN messages

- Templates under `views/attendance_checkin_templates.xml`: success, already, rejected (shared shell).
- Use `request.env` language / `lang` of portal user; wrap all user-visible strings in `_()` and ship `i18n/ar.po` (and `en` source).
- Mobile-first: large status icon, batch name, student name, Present vs Late badge, no admin jargon.
- Login wall must return to QR URL after auth (`redirect` param).
- Prefer RTL layout when `lang` starts with `ar`.

Smoke: switch portal user language AR/EN and hit success + one rejection.

---

## 11. Security considerations (Stable QR, reduce sharing abuse)

Stable QR implies sharing risk. Mitigations **without** rotating QR:

| Control | Detail |
|---------|--------|
| Login required | Attendance only for authenticated portal user. |
| Identity binding | Line always for resolved `op.student`, never for “whoever holds the phone” without account. |
| Enrollment gate | Scanner must be running on that batch. |
| Session window | No check-in outside active session → reduces 24/7 proxy scanning. |
| Duplicate lock | One present line per student/session sheet. |
| Revocation | Inactive flag or regenerate when QR leaked. |
| Rate limit | Cap attempts per user/IP. |
| Audit | Immutable-ish logs with IP + user + result. |
| HTTPS | Ensure `web.base.url` is https in production so QR posts to TLS. |

Out of scope: device binding, selfie, GPS, one-time OTP QR.

---

## 12. Automated tests

### 12.1 Python (`edafaa_batch_attendance/tests/`)

Extend/replace `test_batch_qr_attendance.py` so clocks use **session start**:

| Test | Expect |
|------|--------|
| Enrolled + active session + within grace | `ok`, `present`, `late=False` |
| Same student re-scan | `already`, single line |
| Not enrolled | `rejected_not_enrolled` |
| Inactive QR | `rejected_inactive` |
| Regenerated token | old → `rejected_token`; new → `ok` |
| After grace from session start | `ok`, `late=True` |
| No overlapping session | `no_active_session` |
| User without `user_id` but matching email | resolves + backfills `user_id` |
| Finalize approve sets `user_id` | integration with registration mock/min fixture |

Run:

```bash
# sabry-test example
odoo-bin -d sabry-test --test-enable --stop-after-init -i edafaa_batch_attendance
# or tagged
odoo-bin -d sabry-test --test-tags /edafaa_batch_attendance --stop-after-init
```

### 12.2 Playwright

Path: `/opt/new_kafaat/tests/playwright/meeting_s5/`

| Spec | Coverage |
|------|----------|
| Portal login → scan URL → success | Screenshot |
| Duplicate scan → already | Screenshot |
| Wrong batch enrollment → rejected | Screenshot |
| Optional AR lang smoke | Success page RTL / Arabic string |

Use fixture students with known portal passwords on `sabry-test` only; never create noisy data on TR_K19 beyond smoke.

### 12.3 i18n smoke

Assert Arabic translations loaded for check-in templates (`_()` keys present in `ar.po`).

---

## 13. UAT checklist and evidence

Update `plans/S5_UAT_CHECKLIST.md` to session-based wording. Minimum proof pack under `docs/op_meeting_nabil/evidence/`:

| ID | Scenario | Evidence |
|----|----------|----------|
| U1 | Admin generates QR on batch | Screenshot batch form QR |
| U2 | Download/copy URL | Screenshot / copied URL note |
| U3 | Student portal check-in within 15 min of session start | Present sheet line + portal success png |
| U4 | Check-in after grace | `late=True` line + portal late message |
| U5 | Re-scan | Already message; one line |
| U6 | Non-enrolled portal user | Rejected |
| U7 | Unlinked portal user | `rejected_no_student` |
| U8 | Revoke/regenerate | Old QR fails; new works |
| U9 | No active session | Clear error |
| U10 | AR + EN UI | Two screenshots |

Attach pack to Odoo #49 and reference from OP#358.

---

## 14. Deployment steps

### 14.1 `sabry-test` (build + UAT)

1. Sync module to `/opt/localaddons/edafaa_batch_attendance` (and repo `custom_addons` mirror).
2. Update apps list; install/upgrade `edafaa_batch_attendance`.
3. Confirm `web.base.url` correct for QR.
4. Pick a batch with timetable sessions overlapping UAT time **or** create a test `op.session`.
5. Generate QR; link portal users (`user_id`/email).
6. Run Python tests + Playwright; fill UAT checklist.
7. Keep selection keys and enrollment data untouched beyond linkage backfill.

### 14.2 `TR_K19` (production smoke)

1. Backup / change window per ops SOP.
2. Upgrade module only (no demo data).
3. Spot-check: one non-prod batch **or** controlled training batch — generate QR, one enrolled portal student smoke in window, revoke after.
4. Do **not** mass-regenerate QR on live batches without ops approval.
5. Confirm logs menu works; confirm no attendance sheet collisions with staff “take attendance” same session.

Rollback: uninstall is destructive to QR fields — prefer `attendance_qr_active=False` all batches + module disable.

---

## 15. OpenProject #358 and Odoo #49 delivery / closure

1. Attach this plan on OP#358 + Odoo #49.
2. Implement on `feature/meeting-s5-358`; keep commits scoped to module + tests + docs.
3. Post UAT evidence (screenshots, checklist, test counts).
4. Odoo #49: description/links to PDF or portal evidence if used; mark Done when UAT signed.
5. OP#358: status → Closed / Done; comment with:
   - Module version
   - Design locks reiterated
   - Test results
   - Deploy note sabry-test → TR_K19
6. Update `analysis/WP358_batch_qr_attendance.md` status from stale “NOT IMPLEMENTED” to Done when closed.
7. Update `plans/DEVELOPMENT_PLAN.md` S5 row if needed.
8. Do **not** close if late clock or session resolution still follows day-sheet/`qr_opened_at` drift.

---

## 16. Risks, assumptions, and non-goals

### Assumptions

- Students use phones with camera + browser; portal accounts exist.
- Batches that need QR attendance have (or will have) `op.session` rows for class times.
- OpenEduCat line flags (`present`/`late`) are the official attendance meaning for clients.
- `web.base.url` is reachable from student phones (public HTTPS or VPN as per Kafaat networking).

### Risks

| Risk | Mitigation |
|------|------------|
| Portal user ≠ student partner / empty `user_id` | Resolver + finalize backfill + optional TR_K19 backfill script |
| No timetable sessions | Measure early; operational session creation or approved minimum fix (§5.3) |
| Staff session sheet vs QR sheet collision | Always key sheets by `session_id`; never create competing `session_id=False` sheet for same day as primary path |
| QR photograph sharing | Login + enrollment + session window + revoke |
| Timezone skew on late | Use Odoo datetime with batch/company TZ consistently in tests |
| Dual trees (`localaddons` vs `custom_addons`) | Deploy from one source of truth; sync on merge |

### Explicit non-goals (S5)

- Biometric, GPS/geofencing, NFC  
- Rotating / daily / per-session QR codes  
- Classroom kiosk / shared tablet mode  
- New independent attendance models  
- Auto-mark entire roster absent/present for non-scanners (staff tools remain separate)  
- Enterprise barcode/kiosk modules  
- Changing course/batch/student master-data selection keys  
- Full bilingual redo of unrelated SIS screens (S4)

---

## Implementation phases (execution order)

| Phase | Deliverable | Exit criteria |
|-------|-------------|----------------|
| **P0** | Measure session coverage + linkage gaps on sabry-test | **Done** — BLOCKED session coverage → remediation **Option A locked** ([P0](../analysis/S5_358_P0_FOUNDATION_VALIDATION.md)) |
| **P1** | Session-based service finalized (no `session_id=False` QR path) | In progress with Option A |
| **P2** | Unique email/partner resolve + finalize backfill | In progress |
| **P3** | Portal AR (`ar_001`) / EN UX | In progress |
| **P4** | Admin QR UX (copy/regenerate/logs) | In progress |
| **P5** | Tests + UAT with controlled test session | In progress |

---

## Developer file map

| File | Responsibility |
|------|----------------|
| `models/op_batch.py` | Token, QR compute, generate/regenerate/active |
| `models/attendance_sheet.py` (service) | Resolve student, enrollment, **session**, sheet ensure, late, process_checkin |
| `models/student_registration.py` | Finalize `user_id` backfill |
| `models/checkin_log.py` | Audit + attempts |
| `controllers/attendance_qr.py` | Portal route |
| `views/op_batch_views.xml` | Admin UI |
| `views/attendance_checkin_templates.xml` | Portal pages |
| `views/checkin_log_views.xml` | Log menu |
| `security/ir.model.access.csv` | Access |
| `i18n/ar.po` | Arabic |
| `tests/test_batch_qr_attendance.py` | Unit/integration |
| `tests/playwright/meeting_s5/` | Portal E2E |

---

## Definition of Done

- [ ] Locks honored: portal-only, stable QR, late from **session start + 15m**, duplicate blocked  
- [ ] Attendance written only to `op.attendance.*` with `session_id` set for QR path  
- [ ] Linkage gap minimized (resolver + finalize)  
- [ ] Error matrix §8 implemented and logged  
- [ ] Admin can view/copy/download/regenerate/revoke QR  
- [ ] AR/EN portal messages  
- [ ] Python + Playwright green on sabry-test  
- [ ] UAT evidence attached  
- [ ] Upgrade note executed on TR_K19 (or scheduled with ops sign-off)  
- [ ] OP#358 and Odoo #49 closed with delivery comment  

---

*This document supersedes `PLAN_WP358.md` for execution. P0 remediation is locked to **Option A** (operational session requirement). Do not close #358/#49 until the delivery gate in [S5_UAT_CHECKLIST.md](S5_UAT_CHECKLIST.md) passes.*
