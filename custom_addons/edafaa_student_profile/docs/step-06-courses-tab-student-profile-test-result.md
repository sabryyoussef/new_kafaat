# Step 6 — Courses Tab — Test Results

**Step:** 6  
**Database:** `sabry-test`  
**Date:** 2026-06-07  
**Script:** `/opt/docs/student_profile/step-06-run-tests.py`  
**Command:** `odoo shell -c /etc/odoo/odoo.conf -d sabry-test < /opt/docs/student_profile/step-06-run-tests.py`

---

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 7 |
| Passed | 7 |
| Failed | 0 |
| Blocked/deferred | 0 |

**Result:** All tests passed.

---

## Test log

| Test | Description | Status | Evidence |
|------|-------------|--------|----------|
| T6.1 | Form opens; Courses tab present | **PASS** | `name="courses"`, readonly list |
| T6.2 | No enrollments → empty list | **PASS** | 0 rows |
| T6.3 | Running enrollment row | **PASS** | course, batch, roll, `running` |
| T6.4 | Finished enrollment | **PASS** | `finished` |
| T6.5 | Multiple enrollments | **PASS** | 2 rows |
| T6.6 | Step 5 Training Summary | **PASS** | `active`, run=1, fin=1 |
| T6.7 | Module installed | **PASS** | upgrade OK |

---

## Optional columns

`academic_years_id` and `academic_term_id` included in list arch — no view load errors on `sabry-test`.

---

## Upgrade evidence

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test -u edafaa_student_profile --stop-after-init
# exit_code: 0
```
