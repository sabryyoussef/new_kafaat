# Step 1 — Auto Course Code `CRS-XXXX` — Test Results

**Step:** 1  
**Database:** `sabry-test`  
**Date:** 2026-06-07  
**Runner:** `odoo shell` + `/opt/docs/student_profile/step-01-run-tests.py`  
**Evidence JSON:** `/opt/docs/student_profile/step-01-test-evidence.json`

---

## Summary

| Metric | Value |
|--------|------:|
| Tests executed | 8 |
| Passed | 8 |
| Failed | 0 |
| Ready to commit | **Yes** (pending human commit approval) |

---

## Results

### T1.1 — Create without code → `CRS-0001`

```
TEST RESULT
Step: 1
Test Case: T1.1
Expected: CRS-0001
Actual: CRS-0001
Status: PASS
Screenshot/Log: step-01-test-evidence.json
Notes: create({'name': 'STEP1-TEST-Auto 1'}) only
```

### T1.2 — Second auto → `CRS-0002`

```
TEST RESULT
Step: 1
Test Case: T1.2
Expected: CRS-0002
Actual: CRS-0002
Status: PASS
Screenshot/Log: step-01-test-evidence.json
Notes: Sequential increment confirmed
```

### T1.3 — Manual code `CUSTOM-01` preserved

```
TEST RESULT
Step: 1
Test Case: T1.3
Expected: CUSTOM-01
Actual: CUSTOM-01
Status: PASS
Screenshot/Log: step-01-test-evidence.json
Notes: Sequence not consumed for manual code (next auto = CRS-0003)
```

### T1.4 — Whitespace code → sequence generated

```
TEST RESULT
Step: 1
Test Case: T1.4
Expected: CRS-0003
Actual: CRS-0003
Status: PASS
Screenshot/Log: step-01-test-evidence.json
Notes: code='   ' treated as empty
```

### T1.5 — Duplicate manual code blocked

```
TEST RESULT
Step: 1
Test Case: T1.5
Expected: Uniqueness constraint blocks duplicate
Actual: UniqueViolation on second CUSTOM-DUP create
Status: PASS
Screenshot/Log: step-01-test-evidence.json
Notes: savepoint rollback; existing _unique_course_code constraint
```

### T1.6 — Form view loads

```
TEST RESULT
Step: 1
Test Case: T1.6
Expected: get_views form OK, no view error
Actual: get_views form OK
Status: PASS
Screenshot/Log: odoo shell output
Notes: Includes edafaa form inherit with placeholder
```

### T1.7 — Search/list regression

```
TEST RESULT
Step: 1
Test Case: T1.7
Expected: search_count CRS-0001=1, list returns CRS rows
Actual: search_count CRS-0001=1, list=3
Status: PASS
Screenshot/Log: step-01-test-evidence.json
Notes: Tree/search views unchanged
```

### T1.8 — Install/upgrade module

```
TEST RESULT
Step: 1
Test Case: T1.8
Expected: Module installed, sequence edafaa.op.course prefix CRS-
Actual: state=installed, seq=edafaa.op.course, prefix=CRS-
Status: PASS
Screenshot/Log: install + upgrade --stop-after-init exit 0
Notes: Single ir.sequence row (id=32); noupdate prevents duplicate on upgrade
```

---

## Additional verification

| Check | Result |
|-------|--------|
| `odoo -u edafaa_student_profile --stop-after-init` | Exit 0 |
| PostgreSQL `ir_sequence` for `edafaa.op.course` | 1 row, prefix `CRS-` |
| Legacy backfill | None performed |

---

## Test harness note

Script resets PostgreSQL-backed sequence via `seq.write({'number_next': 1})` before assertions so expected codes start at `CRS-0001`. Direct SQL `UPDATE ir_sequence.number_next` alone does **not** reset Odoo `standard` implementation counters.

---

*All Step 1 tests passed. Awaiting commit approval.*
