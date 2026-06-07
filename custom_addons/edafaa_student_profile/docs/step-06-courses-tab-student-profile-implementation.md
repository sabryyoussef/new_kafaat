# Step 6 — Courses Tab in Student Profile — Implementation

**Step:** 6  
**Requirement:** F — Courses Tab in Student Profile  
**Date:** 2026-06-07  
**Status:** Implemented — awaiting commit approval  
**Approvals:** Step 6 analysis ✓ | Step 6 implementation ✓

---

## Scope delivered

| Item | Done |
|------|------|
| **Courses** notebook tab on default student form | Yes |
| Readonly `course_detail_ids` embedded list | Yes |
| Columns: course, batch, roll number, state | Yes |
| Optional: `academic_years_id`, `academic_term_id` | Yes (included safely) |
| View-only — no new model fields | Yes |
| No `openeducat_library` dependency | Yes |
| Certificate columns | No (Step 8) |

---

## Files changed

| File | Change |
|------|--------|
| `views/student_views.xml` | Courses page; priority 35 |
| `docs/step-06-courses-tab-student-profile-implementation.md` | **New** |
| `docs/step-06-courses-tab-student-profile-test-result.md` | **New** |

---

## View detail

Inherits `openeducat_core.view_op_student_form`.

**Tab order:** Family → **Courses** → Other Information

```xml
<page string="Courses" name="courses">
    <field name="course_detail_ids" readonly="1">
        <list create="false" edit="false" delete="false">
            course_id, batch_id, roll_number, state (badge),
            academic_years_id (optional), academic_term_id (optional)
        </list>
    </field>
</page>
```

**Readonly rule:** Display-only; enrollment create/edit/delete via existing OpenEduCat **Student Course Details** menu and admission/batch workflows.

**Step 5:** Training Summary unchanged on sheet — uses same `course_detail_ids` for aggregate status.

---

## Upgrade

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test -u edafaa_student_profile --stop-after-init
```

---

## Out of scope

- Step 7 skills, Step 8 certificates
- Inline enrollment editing
- `openeducat_library` Educational tab
- New Python model logic
