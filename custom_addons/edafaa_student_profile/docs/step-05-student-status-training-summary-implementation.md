# Step 5 — Student Status and Training Summary — Implementation

**Step:** 5  
**Requirement:** E — Student Status and Training Summary on `op.student`  
**Date:** 2026-06-07  
**Status:** Implemented — awaiting commit approval  
**Approvals:** Step 5 analysis ✓ | Step 5 implementation ✓

---

## Scope delivered

| Item | Done |
|------|------|
| Computed `training_status` on `op.student` | Yes |
| `current_course_id` / `current_batch_id` | Yes |
| `running_course_count` / `completed_course_count` | Yes |
| Training Summary group on student form | Yes |
| Source: `course_detail_ids` / `op.student.course` | Yes |
| Courses tab (Step 6) | No |
| New manifest dependencies | No |

---

## Files changed

| File | Change |
|------|--------|
| `models/student.py` | `_compute_training_summary` + 5 fields |
| `views/student_views.xml` | Training Summary group; priority 30 |
| `docs/step-05-student-status-training-summary-implementation.md` | **New** |
| `docs/step-05-student-status-training-summary-test-result.md` | **New** |

---

## Lifecycle logic

| Condition | `training_status` | Label |
|-----------|-------------------|-------|
| No `course_detail_ids` | `new` | New Trainee |
| Any enrollment `state = running` | `active` | Currently Registered |
| No running, ≥1 `finished` | `completed` | Completed |
| Mixed running + finished | `active` | Currently Registered |
| Enrollments with unknown `state` only | `new` | Safe fallback |

### Current course/batch

- Taken from **running** enrollments only.
- **Primary enrollment** = highest `id` among running rows (latest created).
- If no running enrollment → `current_course_id` and `current_batch_id` empty.

---

## View

**Training Summary** group after bilingual name fields:

- `training_status` (badge)
- `current_course_id`, `current_batch_id`
- `running_course_count`, `completed_course_count`

Family tab (Step 4) unchanged.

---

## Upgrade

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test -u edafaa_student_profile --stop-after-init
```

---

## Out of scope

- Courses tab (Step 6)
- `student_lifecycle_dashboard`, `openeducat_admission`, `openeducat_library`
- Portal, skills, certificates, siblings logic changes
