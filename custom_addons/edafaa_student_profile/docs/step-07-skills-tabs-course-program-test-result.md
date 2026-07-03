# Step 7 — Skills Tabs — Test Results

**Step:** 7  
**Database:** `sabry-test`  
**Date:** 2026-06-07  
**Command:** `odoo shell -c /etc/odoo/odoo.conf -d sabry-test` (inline test block)

---

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 12 |
| Passed | 12 |
| Failed | 0 |
| Blocked/deferred | 0 |

**Result:** All tests passed.

---

## Upgrade evidence

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test -u edafaa_student_profile --stop-after-init
# exit_code: 0
```

---

## Test log

| Test | Description | Status | Evidence |
|------|-------------|--------|----------|
| T7.1 | Create skill successfully | **PASS** | `edafaa.skill` id=1, code `S7-LEAD` |
| T7.2 | Add skills to course | **PASS** | `CRS-0001` → 2 skills assigned |
| T7.3 | Course skills persist after reload | **PASS** | `skill_ids` ids `[1, 2]` |
| T7.4 | Course Subjects tab unchanged | **PASS** | `name="subject"`, `subject_ids` in arch |
| T7.4b | Course Skills tab present | **PASS** | `name="skills"`, `skill_ids` in arch |
| T7.5 | Add skill to program | **PASS** | `PRG-0001` → 1 skill |
| T7.6 | Program skills persist after reload | **PASS** | `skill_ids` ids `[1]` |
| T7.7 | Program form arch (notebook + Skills) | **PASS** | No view error; notebook + skills page |
| T7.8a | Back office create/write skills | **PASS** | Ephemeral BO user; create+write True |
| T7.8b | Faculty read skills | **PASS** | Ephemeral faculty user; read True |
| T7.8c | Faculty cannot create skills | **PASS** | `AccessError` on create attempt |
| T7.8d | Faculty can write courses | **PASS** | Can assign existing skills on course |
| T7.9 | Module installed after upgrade | **PASS** | `edafaa_student_profile` state=installed |

---

## ACL verification

| Access rule | Group | R/W/C/U |
|-------------|-------|---------|
| `access_edafaa_skill_user` | Role / User (internal) | 1/0/0/0 |
| `access_edafaa_skill_faculty` | User (OpenEduCat Faculty) | 1/0/0/0 |
| `access_edafaa_skill_back_office` | Manager (Back Office Admin) | 1/1/1/1 |

---

## Test fixtures used

| Record | Notes |
|--------|-------|
| Skills | `Step7 Test Leadership` (S7-LEAD), `Step7 Test Communication` (S7-COMM) |
| Course | Existing `CRS-0001` (id=20) |
| Program | Existing `PRG-0001` (id=1) |

Ephemeral users `t7_bo_test_step7` / `t7_faculty_test_step7` created for T7.8 and removed after test.

---

## Menu

`edafaa_student_profile.menu_edafaa_skill` registered as **Skills** under Configuration → Course Management.
