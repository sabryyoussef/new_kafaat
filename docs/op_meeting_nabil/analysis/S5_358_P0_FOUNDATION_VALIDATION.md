# S5 P0 — Foundation Validation Report (OP#358 / Odoo #49)

**Date:** 2026-07-15  
**Databases inspected:** `sabry-test` (primary), `TR_K19` (smoke comparison)  
**Code inspected:** `/opt/localaddons/edafaa_batch_attendance`, `/opt/localaddons/openeducat_attendance`, `/opt/localaddons/openeducat_timetable`, `/opt/localaddons/student_enrollment_portal`  
**Scope:** Read-only validation — no P1 coding in this task  
**Plan reference:** [IMPLEMENTATION_PLAN_S5_WP358.md](../plans/IMPLEMENTATION_PLAN_S5_WP358.md)

---

## 0. Remediation decision (locked)

> **Session remediation decision: Option A — Operational Session Requirement.**

A valid `op.session` must exist for the batch and cover the current class/check-in time before QR attendance can succeed. S5 will **not** auto-create sessions, will not use `session_id=False` as the QR primary path, and will not use `qr_opened_at` as the late clock.

**Chosen:** 2026-07-15 · Enables P1–P5 under this constraint. Re-measure coverage after staff schedule sessions for UAT batches.

---

## 1. Executive result

### **BLOCKED — SESSION FOUNDATION** *(at time of P0 measurement)*

| Gate | Result |
|------|--------|
| Timetable / `op.session` coverage for QR-target batches | **BLOCKED** |
| Portal user ↔ `op.student` linkage (resolver + finalize) | **PASS (with minimum fix)** |
| Locked algorithm viability *when sessions exist* | Technically sound |
| Go for unrestricted P1 as production-ready without remediation | **NO-GO** |

**Summary:** The locked flow (QR → student → running enrollment → **active `op.session`** → register/sheet/`session_id` → line; late = `session.start_datetime + 15m`) is implementable in code and already sketched in the current module, but **QR-target batches on sabry-test and TR_K19 generally lack usable timetable sessions**. P1 must not silently fall back to `session_id=False` / `qr_opened_at`. A **session-foundation remediation must be chosen and recorded on OP#358** before treating S5 as production-ready.

**Identity is not a hard block:** when a portal user exists, `user_id` / shared partner / unique email mapping is safe on these DBs (no ambiguous email matches found). Coverage of `user_id` is low mainly because most enrolled students **have no portal user yet**, which is expected for portal check-in.

> Do **not** close OP#358 or Odoo #49 on this report alone.

---

## 2. Database counts

### 2.1 `sabry-test` (primary)

| Metric | Count |
|--------|------:|
| `op.batch` total / active | 3 / 3 |
| `op.student.course` state=`running` | 6 |
| Distinct batches with running enrollment | **2** (ids **24**, **29**) |
| `op.session` total | **1** |
| Running-enrollment batches **with** ≥1 session | **1** (batch **29**) |
| Running-enrollment batches **with no** session | **1** (batch **24**) |
| Active batches with ≥1 session | 1 |
| Active batches with no session | 2 |
| Sessions overlapping “now” at inspection time | 1 (session **25**, batch 29) |
| Overlapping session pairs (same batch, ambiguous) | **0** |
| `op.attendance.register` | 1 |
| `op.attendance.sheet` total | 2 |
| Sheets with `session_id` set | **1** |
| Sheets with `session_id=False` | **1** |
| Students total | 10 |
| Students with `user_id` | 2 |
| Running-enrollment students | 6 |
| Running-enrollment students with `user_id` | **1** |
| Running-enrollment students without `user_id` | **5** |
| `edafaa_batch_attendance` module | installed **19.0.1.1.0** |
| Check-in logs | 4 |

### 2.2 `TR_K19` (comparison smoke)

| Metric | Count |
|--------|------:|
| `op.batch` | 6 |
| Running enrollments | 12 |
| Distinct running batches | 3 |
| `op.session` | **1** |
| Running batches with ≥1 session | **1** |
| Running batches with no session | **2** |
| Attendance sheets | 1 (with `session_id`) |
| Running-enrollment students with `user_id` | **1 / 11** |

TR_K19 confirms the same pattern: timetable usage for attendance windows is thin; portal linkage coverage is low.

---

## 3. Sample record evidence (`sabry-test`)

### Batches with running enrollment

| Batch id | Name / code | Sessions | Notes |
|----------|-------------|----------|-------|
| **24** | UAT PW Running Batch / `UAT-PW-RUN` | **0** | Real UAT target; **no** timetable → locked QR path would return `no_active_session` |
| **29** | S5 PW Batch / `S5PW1` | **1** | Created for S5 Playwright; only covered batch |

### Sole session (id 25)

| Field | Value |
|-------|-------|
| `batch_id` | 29 — S5 PW Batch |
| `course_id` | present |
| `start_datetime` | 2026-07-15 17:41:42 |
| `end_datetime` | 2026-07-15 19:16:42 |
| `state` | `confirm` |
| `active` | True |

Fields required by the locked algorithm are populated on this record. No missing `batch_id` / `course_id` / datetimes across the session set (n=1).

### Attendance sheets

| Sheet id | `session_id` | Date | State | Register |
|----------|--------------|------|-------|----------|
| 4 | **False** | 2026-07-15 | start | QR29 |
| 21 | **25** (session) | 2026-07-15 | start | QR29 |

Shows mixed history: one day-sheet without session (older scaffold path), one session-linked sheet (current path).

### Enrollment / student samples (running)

| Student | Email | `user_id` | Resolvable without portal account? |
|---------|-------|-----------|-------------------------------------|
| 80 | uat-pw-a@uat-pw.test | empty | No matching `res.users` |
| 113–116 | p2.student.*@kafaat.test | empty | No matching `res.users` |
| **228** | s5.pw.student@test.local | **set** (portal) | Yes — happy path |

### Registration records

Only 2 `student.registration` rows, both `draft`, `student_id` empty — no finalized enrollment-portal sample on sabry-test to prove live partner-split, but **source code proves** the split risk (see §6).

---

## 4. Session coverage analysis

### Field reliability (`op.session`)

On inspected data, when sessions exist they reliably include:

- `batch_id`, `course_id`
- `start_datetime`, `end_datetime`
- usable `state` (`confirm` observed; model also has `draft` / `done` / `cancel`)

Selection usable for active window (plan): `state in ('draft','confirm','done')`, exclude `cancel`, require `active`, `start ≤ now ≤ end`.

### Ambiguity

- Overlapping session pairs on the same batch: **0** on sabry-test.
- Risk remains theoretical if staff schedule concurrent sessions; resolver should keep “earliest `start_datetime`” tie-break (already in plan).

### Consistency of attendance sheets vs `session_id`

- Foundation supports both: session-linked sheets and `session_id=False`.
- sabry-test currently **50/50** on existing sheets — evidence of prior day-sheet QR path.
- Locked S5 path must **only** create/use sheets with `session_id` set.

### Locked algorithm viability

```text
QR scan
→ resolve batch
→ resolve logged-in student
→ verify running enrollment
→ find active op.session          ← FAILS for batch 24 / most TR_K19 running batches today
→ find/create register
→ find/create sheet (session_id)
→ write line
Late = session.start_datetime + 15 minutes
```

| Step | Viable on sabry-test? |
|------|------------------------|
| Batch + enrollment gates | Yes |
| Active session resolution | **Only for batches that have timetable** (1/2 running batches) |
| Session-linked sheet + line | Yes when session exists (sheet 21 proves) |
| Late from session start | Yes when session exists; **must not** use `qr_opened_at` |

**Conclusion:** Algorithm is correct; **session data coverage is insufficient** for declaring foundation PASS.

---

## 5. Student ↔ portal user linkage analysis

### Coverage (`sabry-test`)

| Population | With `user_id` | Without |
|------------|----------------:|--------:|
| All students (10) | 2 | 8 |
| Running enrollment (6) | 1 | 5 |

### Resolver probe (students without `user_id`)

| Strategy | Count (all students w/o user_id) |
|----------|----------------------------------:|
| Shared `partner_id` with a `res.users` | **0** remaining (the 2 linked students already have `user_id`) |
| Unique email/login → exactly one user | **0** |
| Ambiguous email → multiple users | **0** |
| No matching user at all | **8** |

Interpretation: failure mode is **“no portal account”**, not **“unsafe multi-match”**. Automatic backfill by unique email is **safe** on this DB (no duplicate login/email collisions observed). Partner mismatch when `user_id` already set: **0**.

### Proposed resolver — validation

```text
1. op.student.user_id = current user
2. else partner_id = user's partner
3. else unique email/login match
4. backfill user_id when match is safe (unique)
5. else rejected_no_student
```

| Step | Verdict |
|------|---------|
| 1 | Correct primary key |
| 2 | Works when portal user reuses student partner (OpenEduCat `create_student_user`); **fails** after enrollment-portal partner split |
| 3 | Works when login/email equals student email and is unique — covers partner-split case |
| 4 | Safe on sabry-test/TR_K19 samples (no ambiguous emails) |
| 5 | Correct for students without portal users |

### Registration finalization — minimum code point

File: `student_enrollment_portal/models/student_registration.py`

1. `action_final_approve` creates student via `_create_student_record()` then portal user via `_create_portal_user()`.
2. `_create_student_record` attaches/reuses partner by **registration email**.
3. `_create_portal_user` **creates a new `res.partner`** for the user and **does not** set `op.student.user_id`.

**Minimum link point (already present in scaffold):**  
`edafaa_batch_attendance/models/student_registration.py` → override `action_final_approve` after `super()`, search `res.users` by `login == record.email`, write `student.user_id` if empty.

Also recommend (P1, still minimum): prefer reusing the student partner when creating the portal user — optional hardening beyond backfill; not required to unblock if step 3 email resolve remains.

### Identity gate

**Not BLOCKED — IDENTITY LINKAGE.** Resolver + finalize backfill is sufficient. Ops may still need a one-time backfill script for historical students who already have portal users but empty `user_id` (none found that need it except via email when accounts exist).

---

## 6. Existing scaffold drift analysis

Module: `edafaa_batch_attendance` **19.0.1.1.0** (installed on sabry-test).

### Already implemented / reusable

| Piece | Status |
|-------|--------|
| Stable QR token / URL / image on `op.batch` | Done |
| Generate / regenerate / active toggle | Done |
| Portal route `/attendance/batch/<token>` `auth=user` | Done |
| Enrollment `running` gate | Done |
| `resolve_student_from_user` (user → partner → email + backfill) | Done |
| Finalize `user_id` link | Done |
| Check-in audit log + rate limit | Done |
| Admin batch QR UI | Done |
| Arabic `i18n/ar.po` | Present |
| Depends on `openeducat_timetable` | Present |

### Historical drift (must stay fixed for locks)

| Behavior | Old day-sheet scaffold | Locked S5 | Current code (19.0.1.1.0) |
|----------|------------------------|-----------|----------------------------|
| Sheet container | `ensure_today_sheet`, `session_id=False` | Sheet linked to active `op.session` | Uses `resolve_active_session` + `ensure_session_sheet` |
| Late clock | `qr_opened_at + grace` | `session.start_datetime + 15m` | `is_late_for_session` |
| Missing session | Implicit create day sheet | `no_active_session` | Returns `no_active_session` |
| `qr_opened_at` field | Late clock | Audit only | Field kept; **not** used for late |

**Evidence of old path still in data:** attendance sheet id **4** with `session_id=False` on register QR29.

### Tests

Current `tests/test_batch_qr_attendance.py` already expects session-based behavior (`_make_active_session`, asserts `sheet.session_id`, `test_no_active_session`, late from session start). **No remaining unit tests encode day-sheet/`qr_opened_at` late** in the current tree. Playwright fixture creates an active session for batch `S5PW1`.

### What must still change for locked S5 (after remediation decision)

| Item | Action |
|------|--------|
| Session coverage | Product/ops remediation (see §8) — **blocker** |
| Do not reintroduce `session_id=False` primary path | Keep current session-linked ensure |
| Do not use `qr_opened_at` for late | Keep current `is_late_for_session` |
| Optional: stop writing `qr_opened_at` or document as audit | Cleanup only |
| Optional: harden `_create_portal_user` to reuse student partner | Nice-to-have identity |
| Optional: historical sheet migration | Ignore old `session_id=False` sheets; do not merge blindly |

**Do not fork a parallel attendance ledger.** Continue extending `op.attendance.*`.

---

## 7. Exact code / model gaps

| Gap | Location | Severity |
|-----|----------|----------|
| QR-target batches lack `op.session` | Data (batch 24 sabry-test; 2/3 running batches TR_K19) | **Blocker** for real UAT on those batches |
| Enrollment portal creates separate partner + no `user_id` | `student_enrollment_portal` `_create_portal_user` | Mitigated by module finalize backfill + email resolve |
| Low portal-user coverage among enrolled students | Data | Expected until portal accounts exist; check-in correctly `rejected_no_student` |
| Legacy day sheet without session | `op.attendance.sheet` id 4 | Do not use for new QR writes |
| `qr_opened_at` still stored | `op.attendance.sheet` inherit | Non-blocking if unused for late |

---

## 8. Recommended minimum remediation (sessions)

### **LOCKED: Option A — Operational (2026-07-15)**

Require staff to create/confirm an `op.session` for the batch covering class time **before** students scan. QR returns clear `no_active_session` otherwise.

- Pros: matches locked design; no new models; no auto-create on TR_K19  
- Cons: timetable discipline required  

### Option B — not selected for S5

Minimal session helper was **not** chosen.

### Explicitly rejected remediations

- Daily sheet with `session_id=False` as primary path  
- Late from `qr_opened_at`  
- Parallel attendance models  
- Kiosk / GPS / rotating QR  
- Automatic session creation on production (TR_K19)
---

## 9. Final go / no-go for P1

| Question | Answer |
|----------|--------|
| May P1 continue refining code against locked session-start design? | **Conditional** — code path is aligned; **do not** declare foundation PASS |
| May P1 ship / close #358 without session remediation decision? | **NO-GO** |
| Identity work for P1 | Proceed with resolver + keep finalize backfill; optional partner reuse |
| Decision gate label | **BLOCKED — SESSION FOUNDATION** |

### Recommended next messages on OP#358 / Odoo #49

1. Attach this report.  
2. Ask product: **Option A or B** for batches without timetable.  
3. After choice: execute remediation (ops process or helper), then re-measure P0 session coverage on a real QR-target batch (e.g. batch 24).  
4. Only then continue UAT/closure for P5–P7.

### Clarification about prior code work

An earlier session aligned `edafaa_batch_attendance` to session-based check-in and updated tests. This **P0 report treats that as scaffold state**, not as authorization to close the WP. **P0 result remains BLOCKED on session data coverage.** No further feature coding should proceed until the session remediation is chosen.

---

## Appendix — Inspection commands (reproducible)

Counts collected via XML-RPC against `http://127.0.0.1:8069` DB `sabry-test` / `TR_K19` as admin on 2026-07-15 (~18:03–18:05 UTC). Source review of the files listed in the header.
