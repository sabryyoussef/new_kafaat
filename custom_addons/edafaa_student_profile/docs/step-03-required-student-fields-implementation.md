# Step 3 — Required Student Fields on `op.student` — Implementation

**Step:** 3  
**Requirement:** Required bilingual and profile fields on SIS student  
**Date:** 2026-06-07  
**Status:** Implemented — awaiting commit approval  
**Approvals:** Step 3 analysis ✓ | Step 3 implementation ✓

---

## Scope delivered

| Item | Done |
|------|------|
| `name_arabic` on `op.student` (`required=True`) | Yes |
| `name_english` on `op.student` (`required=True`) | Yes |
| English name sync to `name`, `first_name`, `last_name` | Yes |
| Python validation (whitespace = missing) | Yes |
| Form inherit `openeducat_core.view_op_student_form` | Yes |
| Expose ID, email, phone, birth date, address fields | Yes |
| Portal bilingual mapping | **Deferred Step 3B** |

---

## Files changed

| File | Change |
|------|--------|
| `__manifest__.py` | Added `views/student_views.xml` |
| `models/__init__.py` | Import `student` |
| `models/student.py` | **New** — bilingual fields, sync, validation |
| `views/student_views.xml` | **New** — form inherit with required UX |
| `docs/step-03-required-student-fields-implementation.md` | **New** |
| `docs/step-03-required-student-fields-test-result.md` | **New** |

---

## Implementation detail

### Bilingual fields (`models/student.py`)

- `name_arabic` and `name_english` are stored on `op.student` with `required=True` and `tracking=True`.

### English name sync

When `name_english` is set on **create**, **write**, or **onchange**:

1. `name` (delegated `res.partner` name) ← stripped `name_english`
2. `first_name` ← first whitespace-separated token
3. `last_name` ← remainder after first token (empty string if single token)

**Example:** `John Michael Doe` → `name='John Michael Doe'`, `first_name='John'`, `last_name='Michael Doe'`

**Single token:** `Ahmed` → `first_name='Ahmed'`, `last_name=''`

OpenEduCat inline `first_name` / `last_name` fields remain on the form; they are overwritten when `name_english` changes. Existing bonafide/report flows that read `name` continue to receive the English full name.

### Required field validation

**Create:** `_validate_required_profile_vals()` runs before `super().create()` and raises `ValidationError` with a field list.

**Write:** `@api.constrains` on stored fields re-validates after save; whitespace-only strings count as missing.

**Validated fields:** `name_arabic`, `name_english`, `id_number`, `email`, `phone`, `birth_date`, `street`, `city`, `country_id`.

### Form view (`views/student_views.xml`)

Inherits `openeducat_core.view_op_student_form` (priority 20):

- Arabic Name + English Name group after the student-name header block
- `id_number` before `birth_date`
- `required="1"` on address/contact fields where safe (XML UX; Python enforces regardless)

No full form redesign; siblings, courses, skills, certificates, and lifecycle tabs untouched.

### Portal fix — deferred (Step 3B)

`student_enrollment_portal` is **not installed** on `sabry-test`. Mapping portal `student_name_arabic` / `student_name_english` to `op.student.name_arabic` / `name_english` requires inheriting `student.registration._create_student_record()`, which needs a manifest `depends` on `student_enrollment_portal`.

Adding that dependency would make `edafaa_student_profile` uninstallable on environments without the portal module. Per approval rules, portal mapping is **deferred** to Step 3B (optional separate inherit or bridge module).

---

## Database upgrade

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test -u edafaa_student_profile --stop-after-init
```

---

## Out of scope (confirmed not touched)

- Siblings, courses tab, student lifecycle/status, skills, certificates
- Program/course code logic (Steps 1–2 unchanged)
- Portal ID/address fields
- `student_enrollment_portal` manifest dependency
