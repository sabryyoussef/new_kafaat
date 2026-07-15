# Requirement Analysis — OP#351 / Odoo #42

**Subject:** Search trainees by national ID (`رقم الهوية`)  
**Priority:** High  
**Status:** **PARTIAL**  
**Estimate:** 0.5 day  
**Links:** [OP#351](https://master.tailcf9988.ts.net:10081/work_packages/351) · [Odoo #42](http://127.0.0.1:8069/web#id=42&model=project.task&view_type=form&db=sabry-test)

---

## 1. Client requirement

Enable searching for trainees/students using **national ID** (`رقم الهوية`) in the Students list / search.

## 2. Current system

| Layer | Finding |
|-------|---------|
| Model field | `id_number` exists on `op.student` with Arabic label |
| Form / list | Field shown |
| Search view | **Not searchable** |
| Autocomplete | No `_rec_names_search` / `name_search` including ID |

### Evidence

- Field: `edafaa_student_profile/models/student.py` — `id_number = fields.Char(string='رقم الهوية')`
- Views: `edafaa_student_profile/views/student_views.xml`
- Search inherit: `edafaa_student_profile/views/student_search_views.xml` — certificate / group-by only; **no** `id_number`
- Base OpenEduCat search (`openeducat_core/views/student_view.xml`): `name`, `blood_group` only

## 3. Gap

Field exists and is filled on profiles, but users **cannot filter or quick-search** by national ID.

## 4. Proposed implementation

1. Add `<field name="id_number" string="رقم الهوية"/>` to student search view  
2. Optional: `_rec_names_search = ['name', 'id_number', …]` for Many2one autocomplete  
3. Upgrade `edafaa_student_profile`; UAT on `sabry-test` → TR_K19  

**Module:** `edafaa_student_profile`

## 5. Acceptance criteria

- [ ] Students search bar can filter by `id_number`
- [ ] Works for existing records on staging
- [ ] No regression on other student filters (certificates, current course)

## 6. Open questions

None blocking — optional autocomplete can be deferred.

## 7. Risks

Low. View-only change (+ optional Python name search).
