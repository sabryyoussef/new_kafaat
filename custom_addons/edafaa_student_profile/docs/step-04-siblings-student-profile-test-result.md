# Step 4 — Siblings in Student Profile — Test Results

**Step:** 4  
**Database:** `sabry-test`  
**Date:** 2026-06-07  
**Script:** `/opt/docs/student_profile/step-04-run-tests.py`  
**Command:** `odoo shell -c /etc/odoo/odoo.conf -d sabry-test < /opt/docs/student_profile/step-04-run-tests.py`

---

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 10 |
| Passed | 10 |
| Failed | 0 |
| Blocked/deferred | 0 |

**Result:** All tests passed.

---

## Test log

| Test | Description | Status | Evidence |
|------|-------------|--------|----------|
| T4.1 | Parent P → A and B; A shows B | **PASS** | `sibling_ids` contains B |
| T4.2 | B shows A | **PASS** | `sibling_ids` contains A |
| T4.3 | A does not show itself | **PASS** | Self excluded |
| T4.4 | C with no parent → empty siblings | **PASS** | `[]` |
| T4.5 | C excludes unrelated A/B | **PASS** | No false siblings |
| T4.6a | Add parent to C → sees A and B | **PASS** | `[A, B]` |
| T4.6b | Remove parent from C → empty | **PASS** | `[]` |
| T4.7 | Student form opens; Family tab | **PASS** | `get_views` OK, `family_tab=True` |
| T4.8 | Parent form opens; children listed | **PASS** | `student_ids` = [A, B] |
| T4.9 | Upgrade + `openeducat_parent` in depends | **PASS** | `installed`, deps include parent |

---

## Fixture notes

- `sabry-test` had 0 students/parents before tests.
- Fixture students created with full Step 3 required fields.
- Parent created with `op.parent.relationship` and `res.partner` (`is_parent=True`).
- Cleanup clears `parent_ids` before student unlink (avoids `openeducat_parent` unlink edge case when `user_id` absent).

---

## Upgrade evidence

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test -u edafaa_student_profile --stop-after-init
# exit_code: 0
```
