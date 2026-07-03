# Step 1 — Auto Course Code `CRS-XXXX` — Implementation

**Step:** 1  
**Requirement:** A — Automatic Course Code `CRS-XXXX`  
**Date:** 2026-06-07  
**Status:** Implemented — awaiting commit approval  
**Approvals:** Step 1 analysis ✓ | Step 1 implementation ✓

---

## Scope delivered

| Item | Done |
|------|------|
| Addon `edafaa_student_profile` skeleton | Yes |
| Depends on `openeducat_core` | Yes |
| Reuse `op.course.code` (no new field) | Yes |
| `ir.sequence` `edafaa.op.course` prefix `CRS-` padding 4 | Yes |
| `create()` override only | Yes |
| Empty/false/whitespace → auto code | Yes |
| Manual code preserved | Yes |
| No legacy backfill | Yes |
| Inherit `view_op_course_form` placeholder only | Yes |
| Tree/search unchanged | Yes |

---

## Pre-implementation checklist

- [x] Impacted model: `op.course`
- [x] Impacted view: `openeducat_core.view_op_course_form` (inherit)
- [x] Reused fields: `code`
- [x] New fields: none
- [x] Sequence impact: `data/course_sequence.xml`
- [x] Security impact: none
- [x] Portal impact: none
- [x] Report/email impact: none
- [x] Test scenarios: T1.1–T1.8
- [x] Rollback: uninstall module

---

## Files created

| File | Purpose |
|------|---------|
| `__manifest__.py` | Module metadata, depends `openeducat_core` |
| `__init__.py` | Load models |
| `models/__init__.py` | Load `course` |
| `models/course.py` | `create()` auto-code logic |
| `data/course_sequence.xml` | `ir.sequence` `edafaa.op.course` |
| `views/course_views.xml` | Form placeholder on `code` |

---

## Implementation detail

### `models/course.py`

- `@api.model_create_multi` on `op.course`
- For each `vals`: if `code` missing or whitespace-only → `next_by_code('edafaa.op.course')`
- Always calls `super().create(vals_list)` — compatible with `openeducat_fees` / portal inherits

### `data/course_sequence.xml`

- `noupdate="1"` — sequence not overwritten on upgrade
- `number_next=1`, `padding=4`, `prefix=CRS-`, `company_id=False`

### `views/course_views.xml`

- Inherit priority 20 (after fees/portal inherits)
- Placeholder only — field remains editable for manual override at create time

---

## Database actions performed

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test -i edafaa_student_profile --stop-after-init
odoo -c /etc/odoo/odoo.conf -d sabry-test -u edafaa_student_profile --stop-after-init
```

Module state on `sabry-test`: **installed**

---

## Out of scope (confirmed not touched)

- Program code, student fields, siblings, courses tab, skills, certificates
- `openeducat_core` or other base module files
- Tree/search/pivot views

---

## Analysis reference

`/opt/docs/student_profile/step-01-auto-course-code-analysis.md`
