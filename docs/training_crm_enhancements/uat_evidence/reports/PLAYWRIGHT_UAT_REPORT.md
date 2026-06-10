# Playwright UAT Report — Training CRM Enhancements

## Environment

| Item | Value |
|------|-------|
| Odoo URL | `http://localhost:8069` |
| Database | `sabry-test` |
| Login | `admin` (password via `ODOO_PASSWORD` env — not committed) |
| Branch | `feature/training-program-crm-enhancements` |
| Spec | `tests/playwright/training_crm_enhancements/training_crm_uat.spec.ts` |
| Run date | 2026-06-07 |

## Scenario results

| ID | Scenario | Status | Screenshot |
|----|----------|--------|------------|
| UAT-CRM-01 | Sales Team lead target | **PASS** | [01_crm_lead_target.png](../screenshots/01_crm_lead_target.png) |
| UAT-CRM-02 | CRM Students menu / wording | **PASS** | [02_crm_student_customer_label.png](../screenshots/02_crm_student_customer_label.png) |
| UAT-PROG-01 | Program workflow statusbar | **PASS** | [03_program_workflow_statusbar.png](../screenshots/03_program_workflow_statusbar.png) |
| UAT-PROG-02 | Program Arabic tabs | **PASS** | [04_program_tabs.png](../screenshots/04_program_tabs.png) |
| UAT-PROG-03 | Program enhancement fields | **PASS** | [05_program_fields.png](../screenshots/05_program_fields.png) |
| UAT-PROG-04 | Program Skills regression | **PASS** | [06_program_skills_regression.png](../screenshots/06_program_skills_regression.png) |
| UAT-PROG-05 | Linked courses on program | **PASS** | [07_program_linked_courses.png](../screenshots/07_program_linked_courses.png) |
| UAT-PROG-06 | Marketing and media section | **PASS** | [08_program_marketing_media.png](../screenshots/08_program_marketing_media.png) |
| UAT-REG-01 | Student profile regression | **PASS** | [09_student_profile_regression.png](../screenshots/09_student_profile_regression.png) |

## Summary

| Metric | Count |
|--------|-------|
| Passed | 9 |
| Failed | 0 |
| Skipped | 0 |
| Blocked | 0 |

## Notes

- UAT-CRM-01 opens `crm.team` form via RPC-resolved team ID (Sales Teams action uses kanban dashboard without list rows).
- G2 promo popup dismissed using `.s_popup_close.js_close_popup` pattern from Student Profile UAT.
- Student regression uses fixture `UAT-PW-A` from prior Student Profile branch.

## Recommendation

**Ready for client UAT review** on `feature/training-program-crm-enhancements` after merge review with Product Owner.
