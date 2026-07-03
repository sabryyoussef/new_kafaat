# Step 3B — Portal Required Fields Bridge — Implementation

**Step:** 3B  
**Requirement:** Portal compatibility for required student fields after Step 3  
**Date:** 2026-06-07  
**Status:** Implemented — awaiting commit approval  
**Approvals:** Step 3B analysis ✓ | Step 3B implementation ✓

---

## Scope delivered

| Item | Done |
|------|------|
| New bridge addon `edafaa_student_profile_portal` | Yes |
| Depends on `edafaa_student_profile` + `student_enrollment_portal` only | Yes |
| No changes to `edafaa_student_profile` core | Yes |
| No direct edits to `student_enrollment_portal` | Yes |
| Backend registration fields: `id_number`, `street`, `city`, `country_id` | Yes |
| Override `_create_student_record()` for full `op.student` mapping | Yes |
| Pre-create validation with clear `ValidationError` | Yes |
| Public portal form unchanged | Yes |

---

## Runtime vs git divergence (documented)

| Environment | Portal target model | Bridge applicability |
|-------------|--------------------|-----------------------|
| Runtime `/opt/localaddons` | **`op.student`** | **Supported** — bridge tested here |
| Git `/opt/new_kafaat/custom_addons` | **`gr.student`** | **Requires alignment** — git `student.registration.student_id` points to `gr.student`; bridge creates `op.student`. Install bridge only after git portal is aligned to runtime `op.student` variant. |

**`gr.student` flow:** Unaffected when bridge is not installed or when git portal (without alignment) is used without bridge.

---

## Files created

| File | Purpose |
|------|---------|
| `__manifest__.py` | Addon metadata and dependencies |
| `__init__.py` | Package init |
| `models/__init__.py` | Model imports |
| `models/student_registration.py` | Registration fields, validation, `_create_student_record` override |
| `views/student_registration_views.xml` | Backend “Student Profile Required Data” section |
| `docs/step-03b-portal-required-fields-implementation.md` | This document |
| `docs/step-03b-portal-required-fields-test-result.md` | Test results |

---

## Implementation detail

### Registration fields (`models/student_registration.py`)

Added on `student.registration`:

- `id_number`, `street`, `city`, `country_id`

Editable on backend until student is created (`readonly` when `student_id` set or state rejected).

### Pre-create validation

`_validate_registration_profile_for_student()` checks before `op.student.create()`:

Arabic name, English name, ID number, email, phone, birth date, street, city, country. Whitespace = missing.

### `_create_student_record()` override

Maps registration → `op.student.create()` vals:

| Registration | `op.student` |
|--------------|--------------|
| `student_name_arabic` | `name_arabic` |
| `student_name_english` | `name_english`, `name`, `first_name`, `last_name` (via `op.student._split_english_name`) |
| `email` | `email` |
| `phone` | `phone` |
| `birth_date` | `birth_date` |
| `id_number` | `id_number` |
| `street` | `street` |
| `city` | `city` |
| `country_id` | `country_id` |

Partner record updated/created with same contact/address data. Step 3 `op.student.create()` validation and `name_english` sync run on the final `create()` call.

### View (`views/student_registration_views.xml`)

Inherits `student_enrollment_portal.view_student_registration_form`. Adds group **Student Profile Required Data** after the phone/contact group (field-based xpath for Odoo 19 compatibility).

---

## Install / upgrade

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test -i edafaa_student_profile_portal --stop-after-init
```

Requires `student_enrollment_portal` and `edafaa_student_profile` installed.

---

## Out of scope (confirmed not touched)

- `edafaa_student_profile` core addon
- `student_enrollment_portal` source module
- Public website registration form
- `gr.student` model / grants flow
- Steps 4–8 (siblings, courses, status, skills, certificates)
