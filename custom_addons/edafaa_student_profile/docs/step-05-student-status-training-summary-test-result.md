# Step 5 — Student Status and Training Summary — Test Results

**Step:** 5  
**Database:** `sabry-test`  
**Date:** 2026-06-07  
**Script:** `/opt/docs/student_profile/step-05-run-tests.py`  
**Command:** `odoo shell -c /etc/odoo/odoo.conf -d sabry-test < /opt/docs/student_profile/step-05-run-tests.py`

---

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 9 |
| Passed | 9 |
| Failed | 0 |
| Blocked/deferred | 0 |

**Result:** All tests passed.

---

## Test log

| Test | Description | Status | Evidence |
|------|-------------|--------|----------|
| T5.1 | No enrollments → New Trainee | **PASS** | `training_status=new` |
| T5.2 | Running enrollment → Currently Registered | **PASS** | `training_status=active` |
| T5.3 | Finished only → Completed | **PASS** | `training_status=completed` |
| T5.4 | Running + finished → Currently Registered | **PASS** | `training_status=active` |
| T5.5 | Current course/batch from running row | **PASS** | Matches running enrollment |
| T5.6 | Multiple running → highest ID selected | **PASS** | Higher enroll id wins |
| T5.7 | Running/completed counts | **PASS** | mix 1/1, fin 0/1 |
| T5.8 | Form opens; Training Summary present | **PASS** | `training_summary` in arch |
| T5.9 | Module installed after upgrade | **PASS** | `edafaa_student_profile` installed |

---

## Fixture notes

- Students created with Step 3 required fields.
- `op.course` / `op.batch` fixtures with `start_date` / `end_date`.
- `sabry-test` had 0 students/enrollments before test run.

---

## Upgrade evidence

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test -u edafaa_student_profile --stop-after-init
# exit_code: 0
```
