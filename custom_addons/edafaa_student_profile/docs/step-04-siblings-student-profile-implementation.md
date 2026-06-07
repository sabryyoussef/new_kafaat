# Step 4 — Siblings Visible in Student Profile — Implementation

**Step:** 4  
**Requirement:** D — Siblings visible in Student Profile  
**Date:** 2026-06-07  
**Status:** Implemented — awaiting commit approval  
**Approvals:** Step 4 analysis ✓ | Step 4 implementation ✓

---

## Scope delivered

| Item | Done |
|------|------|
| Extend `edafaa_student_profile` | Yes |
| Dependency `openeducat_parent` | Yes |
| Computed `sibling_ids` on `op.student` | Yes |
| Family notebook tab with `parent_ids` + siblings | Yes |
| `op.parent` model unchanged | Yes |
| Parents stat button preserved | Yes |
| `child_ids` untouched | Yes |

---

## Files changed

| File | Change |
|------|--------|
| `__manifest__.py` | Added `openeducat_parent` dependency |
| `models/student.py` | `sibling_ids` computed Many2many |
| `views/student_views.xml` | **Family** tab; view priority 25 |
| `docs/step-04-siblings-student-profile-implementation.md` | **New** |
| `docs/step-04-siblings-student-profile-test-result.md` | **New** |

---

## Implementation detail

### Sibling logic (`models/student.py`)

```python
sibling_ids = fields.Many2many('op.student', compute='_compute_sibling_ids')

@api.depends('parent_ids', 'parent_ids.student_ids')
def _compute_sibling_ids(self):
    siblings = parent_ids.mapped('student_ids') - self
```

- **Non-stored**, readonly computed Many2many.
- No parents → empty siblings.
- Multiple shared parents → deduplicated via recordset union minus self.

### Family tab (`views/student_views.xml`)

Inherits `openeducat_core.view_op_student_form` (priority 25), inserts page before `other_information`:

| Section | Field | Notes |
|---------|-------|-------|
| Parents | `parent_ids` | `many2many_tags`, `no_create` |
| Siblings | `sibling_ids` | Readonly list: `name_english`, `name_arabic`, `id_number`, `email`, `phone` |

Existing **Parents** stat button from `openeducat_parent` unchanged.

### Upgrade

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test -u edafaa_student_profile --stop-after-init
```

---

## Out of scope (confirmed not touched)

- `op.parent` model/views
- Step 5 status, Step 6 courses tab, skills, certificates
- Portal / Step 3B bridge
- `child_ids` (partner contacts)
