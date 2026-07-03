# Step 8 — Certificate Workflow — Test Results

**Step:** 8  
**Database:** `sabry-test`  
**Date:** 2026-06-09  
**Command:** `odoo shell -c /etc/odoo/odoo.conf -d sabry-test` (inline test block)

---

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 11 |
| Passed | 11 |
| Failed | 0 |
| Blocked/deferred | 0 |

**Result:** All tests passed.

---

## Upgrade evidence

```bash
odoo shell -c /etc/odoo/odoo.conf -d sabry-test
env['ir.module.module'].search([('name','=','edafaa_student_profile')]).button_immediate_upgrade()
# exit_code: 0
```

---

## Test log

| Test | Description | Status | Evidence |
|------|-------------|--------|----------|
| T8.1 | Issue cert for finished enrollment | **PASS** | `state=issued` |
| T8.2 | Running enrollment blocked | **PASS** | `ValidationError` |
| T8.3 | Number from new sequence | **PASS** | `CERT-2026-0008` |
| T8.4 | Duplicate enrollment blocked | **PASS** | `ValidationError` |
| T8.5 | Visible on student profile | **PASS** | `certificate_count=1` |
| T8.6 | Courses tab columns/actions | **PASS** | arch contains cert fields/buttons |
| T8.6b | Finished row shows cert number | **PASS** | matches issued cert |
| T8.7 | PDF report/attachment | **PASS** | `attachment_id` set; print action OK |
| T8.8 | Missing email validation | **PASS** | `ValidationError` after partner email cleared |
| T8.9 | Send email action | **PASS** | `mail.mail` created (`mail_delta=1`); `state=sent` |
| T8.10 | Module installed | **PASS** | `edafaa_student_profile` installed |

---

## SMTP note

`sabry-test` has **0** outgoing mail servers. T8.9 verifies `mail.mail` creation and certificate `email_sent` / `state=sent` — actual SMTP delivery not tested.

---

## Bonafide isolation

Sequence `op.student.certificate` prefix remains `CERT/` — not reused for completion certificates.

---

## Fixtures used

| Record | Notes |
|--------|-------|
| Student `T8-ID-0001` | Step 3–compliant profile |
| Student `T8-ID-0002` | Email cleared on partner for T8.8 |
| Enrollments | Finished (`T8-BATCH-FIN`) + running (`T8-BATCH-RUN`) |
| Course | Existing `op.course` on `sabry-test` |

Test fixtures remain on `sabry-test` for manual verification.
