# Step 2 — Auto Program Code `PRG-XXXX` — Implementation

**Step:** 2  
**Requirement:** B — Automatic Program Code `PRG-XXXX`  
**Date:** 2026-06-07  
**Status:** Implemented — awaiting commit approval  
**Approvals:** Step 2 analysis ✓ | Step 2 implementation ✓

---

## Scope delivered

| Item | Done |
|------|------|
| Extend `edafaa_student_profile` | Yes |
| Reuse `op.program.code` | Yes |
| New program code field | No |
| `ir.sequence` `edafaa.op.program` prefix `PRG-` padding 4 | Yes |
| `create()` override on `op.program` only | Yes |
| Empty/false/whitespace → auto code | Yes |
| Manual code preserved | Yes |
| No `motakamel.program` changes | Yes |
| No legacy backfill | Yes |
| Inherit `view_op_program_form` placeholder only | Yes |
| Tree/search unchanged | Yes |

---

## Files changed

| File | Change |
|------|--------|
| `__manifest__.py` | Added `program_sequence.xml`, `program_views.xml` |
| `models/__init__.py` | Import `program` |
| `models/program.py` | **New** — `create()` auto-code |
| `data/program_sequence.xml` | **New** — sequence `edafaa.op.program` |
| `views/program_views.xml` | **New** — form placeholder on `code` |

---

## Implementation detail

### `models/program.py`

Mirrors Step 1 `course.py`: `@api.model_create_multi` assigns `edafaa.op.program` when `code` empty/whitespace.

### `data/program_sequence.xml`

- `noupdate="1"`
- Separate from `motakamel.program` / `PROG-` sequence

### Database

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test -u edafaa_student_profile --stop-after-init
```

---

## Out of scope (confirmed not touched)

- `motakamel.program`, student fields, siblings, courses tab, skills, certificates
- `openeducat_core` direct edits

## Analysis reference

`/opt/docs/student_profile/step-02-auto-program-code-analysis.md`
