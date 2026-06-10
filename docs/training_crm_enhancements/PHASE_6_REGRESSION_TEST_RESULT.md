# Phase 6 — Regression Test Results

**Database:** `sabry-test`  
**Date:** 2026-06-07  
**Command:** `odoo -d sabry-test -u edafaa_student_profile,edafaa_training_crm --stop-after-init`

## Module upgrade

| Module | Result |
|--------|--------|
| `edafaa_training_crm` | PASS — installed/upgraded |
| `edafaa_student_profile` | PASS — upgraded, no view errors |

## Odoo unit tests (`edafaa_training_crm`)

| Suite | Tests | Failed | Errors |
|-------|-------|--------|--------|
| `test_crm_team` | 3 | 0 | 0 |
| `test_res_partner` | 2 | 0 | 0 |
| `test_op_program` | 3 | 0 | 0 |

**Total: 8 tests, 0 failed, 0 errors**

## Student Profile regression (manual / Playwright)

| Area | Result |
|------|--------|
| Student form opens (`UAT-PW-A`) | PASS |
| Required profile fields visible | PASS |
| Courses tab | PASS |
| Program Skills tab | PASS |
| Certificate workflow data | PASS (prior branch data) |

## Known non-blocking warnings

- `res_partner_unique_email` index creation warning (pre-existing duplicate emails in DB).
- `slide_channel_completed_ids` / `completed_course_count` label collision (pre-existing).

**Phase 6 status: PASS**
