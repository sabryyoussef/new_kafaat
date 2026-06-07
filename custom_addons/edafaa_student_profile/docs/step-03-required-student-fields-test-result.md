# Step 3 — Required Student Fields — Test Results

**Step:** 3  
**Database:** `sabry-test`  
**Date:** 2026-06-07  
**Script:** `/opt/docs/student_profile/step-03-run-tests.py`  
**Command:** `odoo shell -c /etc/odoo/odoo.conf -d sabry-test < /opt/docs/student_profile/step-03-run-tests.py`

---

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 14 |
| Passed | 13 |
| Failed | 0 |
| Deferred | 1 |

**Result:** All executable tests passed. Portal mapping deferred.

---

## Test log

| Test | Description | Status | Evidence |
|------|-------------|--------|----------|
| T3.1 | Create without Arabic name → blocked | **PASS** | `ValidationError: Missing required student profile field(s): Arabic Name` |
| T3.2 | Create without English name → blocked | **PASS** | `ValidationError: Missing required student profile field(s): English Name` |
| T3.3 | Create without ID number → blocked | **PASS** | `ValidationError: ... ID Number` |
| T3.4 | Create without email → blocked | **PASS** | `ValidationError: ... Email` |
| T3.5 | Create without phone → blocked | **PASS** | `ValidationError: ... Phone` |
| T3.6 | Create without birth date → blocked | **PASS** | `ValidationError: ... Birth Date` |
| T3.7a | Create without street → blocked | **PASS** | `ValidationError: ... Street` |
| T3.7b | Create without city → blocked | **PASS** | `ValidationError: ... City` |
| T3.7c | Create without country → blocked | **PASS** | `ValidationError: ... Country` |
| T3.7d | Whitespace-only Arabic name → blocked | **PASS** | `ValidationError: ... Arabic Name` |
| T3.8 | Valid student with all fields → saved | **PASS** | `op.student` id=21 created |
| T3.9 | `name_english` syncs `name`, `first_name`, `last_name` | **PASS** | `John Michael Doe` → `John` / `Michael Doe` |
| T3.10 | Portal Arabic/English mapping | **DEFERRED** | `student_enrollment_portal` not installed; safe optional inherit not possible without manifest `depends` |
| T3.11 | Module upgrade + student form loads | **PASS** | `edafaa_student_profile` installed; `get_views` form OK |

---

## Upgrade evidence

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test -u edafaa_student_profile --stop-after-init
# exit_code: 0
```

---

## Notes

- Pre-create `_validate_required_profile_vals()` ensures T3.1/T3.2 raise `ValidationError` instead of raw SQL `NOT NULL` / partner check errors.
- `sabry-test` had no pre-existing students; full enforcement applied cleanly.
- T3.10 documented as Step 3B follow-up when portal module is installed and dependency strategy is approved.
