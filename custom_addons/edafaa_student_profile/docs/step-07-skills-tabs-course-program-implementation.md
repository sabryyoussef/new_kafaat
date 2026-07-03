# Step 7 — Skills Tabs for Course and Program — Implementation

**Step:** 7  
**Requirement:** G — Skills Tabs for Course and Program  
**Date:** 2026-06-07  
**Status:** Implemented — awaiting commit approval  
**Approvals:** Step 7 analysis ✓ | Step 7 implementation ✓

---

## Scope delivered

| Item | Done |
|------|------|
| New model `edafaa.skill` | Yes |
| `op.course.skill_ids` Many2many | Yes |
| `op.program.skill_ids` Many2many | Yes |
| Course form **Skills** notebook page | Yes (after Subjects) |
| Program form **Skills** notebook page | Yes (new notebook) |
| Subjects tab unchanged | Yes |
| No `hr_skills` / `openeducat_skill_enterprise` dependency | Yes |
| Security `ir.model.access.csv` | Yes |
| Skill master menu under Configuration → Course Management | Yes |

---

## Files changed

| File | Change |
|------|--------|
| `models/skill.py` | **New** — `edafaa.skill` |
| `models/course.py` | `skill_ids` M2M |
| `models/program.py` | `skill_ids` M2M |
| `models/__init__.py` | Import `skill` |
| `security/ir.model.access.csv` | **New** — ACL for `edafaa.skill` |
| `views/skill_views.xml` | **New** — tree, form, search, action, menu |
| `views/course_views.xml` | Skills page inherit |
| `views/program_views.xml` | Notebook + Skills page inherit |
| `__manifest__.py` | Security + skill views in `data` |
| `docs/step-07-skills-tabs-course-program-implementation.md` | **New** |
| `docs/step-07-skills-tabs-course-program-test-result.md` | **New** |

---

## Model detail

### `edafaa.skill`

| Field | Type | Notes |
|-------|------|-------|
| `name` | Char | Required, `translate=True` |
| `code` | Char | Optional |
| `description` | Text | Optional |
| `active` | Boolean | Default `True` |

### Relation tables

| Table | Columns |
|-------|---------|
| `edafaa_course_skill_rel` | `course_id`, `skill_id` |
| `edafaa_program_skill_rel` | `program_id`, `skill_id` |

---

## View detail

### Course (`openeducat_core.view_op_course_form`)

Inherit priority 25 — inserts **Skills** page after `name="subject"`:

```xml
<page string="Skills" name="skills">
    <field name="skill_ids" nolabel="1" widget="many2many_tags"/>
</page>
```

**Subjects** page and `subject_ids` untouched.

### Program (`openeducat_core.view_op_program_form`)

Inherit priority 25 — notebook after main `group[@class='pt-3']`:

```xml
<notebook>
    <page string="Skills" name="skills">
        <field name="skill_ids" nolabel="1" widget="many2many_tags"/>
    </page>
</notebook>
```

### Skill master UI

Menu: **OpenEduCat → Configuration → Course Management → Skills**  
Groups: `openeducat_core.group_op_back_office_admin` only (catalog CRUD).  
Faculty/internal users assign existing skills via course/program M2M fields.

---

## Security

| Group | Read | Write | Create | Unlink |
|-------|------|-------|--------|--------|
| `base.group_user` | ✓ | — | — | — |
| `openeducat_core.group_op_faculty` | ✓ | — | — | — |
| `openeducat_core.group_op_back_office_admin` | ✓ | ✓ | ✓ | ✓ |

Mirrors `op.subject` pattern: internal/faculty read; back office manages catalog.

---

## Upgrade

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test -u edafaa_student_profile --stop-after-init
```

Runtime synced: `/opt/localaddons/edafaa_student_profile/`

---

## Out of scope

- Step 8 certificates
- Skill levels / assessments
- `hr.skill` integration
- Portal display of skills
