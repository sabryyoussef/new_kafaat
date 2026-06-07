# Step 3B — Portal Required Fields Bridge — Test Results

**Step:** 3B  
**Database:** `sabry-test`  
**Date:** 2026-06-07  
**Script:** `/opt/docs/student_profile/step-03b-run-tests.py`  
**Command:** `odoo shell -c /etc/odoo/odoo.conf -d sabry-test < /opt/docs/student_profile/step-03b-run-tests.py`

---

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 9 |
| Passed | 9 |
| Failed | 0 |
| Blocked/deferred | 0 |

**Result:** All tests passed on runtime stack (`op.student` portal variant).

---

## Test log

| Test | Description | Status | Evidence |
|------|-------------|--------|----------|
| T3B.1 | Install/upgrade `edafaa_student_profile_portal` | **PASS** | Module state `installed` |
| T3B.2 | Backend form shows ID/address fields + section title | **PASS** | `id_number`, `street`, `city`, `country_id`, “Student Profile Required Data” in form arch |
| T3B.3 | Finalize blocked when ID/address missing | **PASS** | `ValidationError: Cannot create student record. Missing required profile field(s): ID Number, Street, City, Country` |
| T3B.4 | Complete data creates `op.student` | **PASS** | `model=op.student, id=25` |
| T3B.5 | Arabic name maps to `name_arabic` | **PASS** | `عربي 4` |
| T3B.6 | English name maps and syncs to `name` / parts | **PASS** | `Portal English 4` → `Portal` / `English 4` |
| T3B.7 | Email, phone, birth date mapped | **PASS** | Values match registration |
| T3B.8 | Step 3 required fields present on created student | **PASS** | `required_ok=True` |
| T3B.9 | `edafaa_student_profile` independent of portal | **PASS** | No portal in core depends; core form loads |

---

## Install evidence

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test -i edafaa_student_profile_portal --stop-after-init
# exit_code: 0
```

Initial view xpath using `@string` selector failed on Odoo 19; fixed to `//field[@name='phone']/parent::group` before retest.

---

## Environment notes

- Tests run against **runtime** `/opt/localaddons` portal (`op.student`).
- Git repo portal (`gr.student`) not exercised; bridge install on misaligned git stack documented as requiring environment alignment first (see implementation doc § Runtime vs git divergence).
