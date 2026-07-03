# Step 2 — Auto Program Code `PRG-XXXX` — Test Results

**Step:** 2  
**Database:** `sabry-test`  
**Date:** 2026-06-07  
**Runner:** `odoo shell` + `/opt/docs/student_profile/step-02-run-tests.py`  
**Evidence JSON:** `/opt/docs/student_profile/step-02-test-evidence.json`

---

## Summary

| Metric | Value |
|--------|------:|
| Tests executed | 10 (T2.0 setup + T2.1–T2.9) |
| Passed | 10 |
| Failed | 0 |
| Ready to commit | **Yes** (pending commit approval) |

---

## Results

| ID | Test case | Expected | Actual | Status |
|----|-----------|----------|--------|--------|
| T2.0 | Create program level (setup) | Level exists | `STEP2-TEST- Level` | PASS |
| T2.1 | Program without code | `PRG-0001` | `PRG-0001` | PASS |
| T2.2 | Second auto program | `PRG-0002` | `PRG-0002` | PASS |
| T2.3 | Manual `CUSTOM-PRG-01` | Preserved | `CUSTOM-PRG-01` | PASS |
| T2.4 | Whitespace code | `PRG-0003` | `PRG-0003` | PASS |
| T2.5 | Duplicate manual code | Blocked | `UniqueViolation` | PASS |
| T2.6 | Form view | No error | `get_views form OK` | PASS |
| T2.7 | Search/list | Finds PRG rows | `count=1, list=4` | PASS |
| T2.8 | Upgrade/sequence | Installed, `PRG-` prefix | `edafaa.op.program` | PASS |
| T2.9 | Motakamel unaffected | PROG- logic separate | `motakamel` uninstalled; no DB/model load; addon unchanged | PASS |

### T2.9 note

`motakamel` is **uninstalled** on `sabry-test`. Verified:

- No `motakamel.program` sequence loaded in DB
- `edafaa.op.program` sequence is independent (`PRG-` prefix)
- `motakamel` source files not modified

When `motakamel` is installed, it continues to use `motakamel.program` sequence with `PROG-` on `program_id`.

---

## Test prerequisite

`sabry-test` had 0 `op.program.level` records before tests. Script creates temporary `STEP2-TEST- Level` — not a Step 2 failure.

---

*All Step 2 tests passed. Awaiting commit approval.*
