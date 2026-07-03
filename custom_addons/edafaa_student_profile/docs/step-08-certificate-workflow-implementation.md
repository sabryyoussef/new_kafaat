# Step 8 — Certificate Workflow — Implementation

**Step:** 8  
**Requirement:** H — Certificate Workflow  
**Date:** 2026-06-09  
**Status:** Implemented — awaiting commit approval  
**Approvals:** Step 8 analysis ✓ | Step 8 implementation ✓

---

## Scope delivered

| Item | Done |
|------|------|
| New model `edafaa.student.certificate` | Yes |
| One certificate per finished `op.student.course` enrollment | Yes |
| Sequence `edafaa.student.certificate` (`CERT-%(year)s-` + 4-digit) | Yes |
| Minimal QWeb PDF report + attachment on issue | Yes |
| `mail.template` + send-by-email action | Yes |
| Courses tab integration (Step 6 extension) | Yes |
| Student smart button **Certificates** | Yes |
| Admin menu **Course Certificates** | Yes |
| Bonafide / `gr.certificate` unchanged | Yes |
| Portal download | No (deferred) |

---

## Files changed

| File | Change |
|------|--------|
| `models/certificate.py` | **New** — certificate model + issue/download/email |
| `models/student_course.py` | **New** — enrollment helpers + row actions |
| `models/student.py` | `certificate_ids`, `certificate_count`, smart button action |
| `models/__init__.py` | Imports |
| `data/certificate_sequence.xml` | **New** |
| `data/mail_template.xml` | **New** |
| `reports/certificate_report.xml` | **New** — QWeb PDF |
| `views/certificate_views.xml` | **New** — tree/form/menu |
| `views/student_views.xml` | Courses tab cert columns/buttons; smart button |
| `security/ir.model.access.csv` | Certificate ACL rows |
| `__manifest__.py` | `mail` dependency + new data/views |
| `docs/step-08-certificate-workflow-implementation.md` | **New** |
| `docs/step-08-certificate-workflow-test-result.md` | **New** |

---

## Model summary

### `edafaa.student.certificate`

| Field | Notes |
|-------|-------|
| `certificate_number` | Assigned on issue via sequence |
| `student_id`, `student_course_id` | Required; unique per enrollment |
| `course_id`, `batch_id` | Related from enrollment |
| `issue_date`, `state` | `draft` → `issued` → `sent` |
| `attachment_id` | PDF from report on issue |
| `email_sent`, `email_sent_date` | Email audit |

**Rules:** Create/issue blocked unless enrollment `state == finished`. Duplicate enrollment blocked in Python + SQL constraint.

### `op.student.course` helpers

`certificate_id`, `certificate_number`, `certificate_state`, `can_issue_certificate` + row actions: Issue, Download, Send Email.

### Numbering

| Sequence | Prefix | Purpose |
|----------|--------|---------|
| `edafaa.student.certificate` | `CERT-%(year)s-` | **Step 8 completion certs** |
| `op.student.certificate` | `CERT/` | Bonafide only — **unchanged** |

---

## Views

- **Courses tab:** certificate number + Issue/Download/Send buttons (finished enrollments only).
- **Student form:** Certificates stat button when count > 0.
- **Menu:** Students → Configuration → Course Certificates (back office).

---

## Report & email

- **Report:** `Course Completion Certificate` — simple completion layout (English/Arabic name, course, batch, number, date).
- **Email:** `mail.template` `Student Course Certificate` — attaches issued PDF; `ValidationError` if student email missing.
- **SMTP:** `sabry-test` has 0 outgoing servers — `mail.mail` record created; delivery requires SMTP config.

---

## Upgrade

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test -u edafaa_student_profile --stop-after-init
```

Runtime synced: `/opt/localaddons/edafaa_student_profile/`

---

## MVP limitations (documented)

- PDF branding is minimal — client design sign-off deferred.
- No skill list on certificate (Step 7 tags not printed).
- No portal download for `op.student`.
- No public verification URL.
