# Requirement Analysis — OP#357 / Odoo #48

**Subject:** Full Arabic UI translation  
**Priority:** Low  
**Status:** **PARTIAL**  
**Estimate:** 2–4 weeks (scope-dependent)  
**Links:** [OP#357](https://master.tailcf9988.ts.net:10081/work_packages/357) · [Odoo #48](http://127.0.0.1:8069/web#id=48&model=project.task&view_type=form&db=sabry-test)

---

## 1. Client requirement

**Complete Arabic translation** of the user interface for Kafaat users.

## 2. Current system

| Layer | State |
|-------|-------|
| OpenEduCat (`localaddons`) | `ar_001.po` present; high fill rate |
| Motakamel | `ar.po` (not always `ar_001`) |
| Edafaa modules | **No `i18n/`** in `custom_addons` or `localaddons` |
| Student screens | Mixed: hardcoded Arabic in some XML/Python; English elsewhere |

Hardcoded Arabic examples: `رقم الهوية`, `التخصص` in `edafaa_student_profile` — breaks proper `_()` / language switch for EN users.

## 3. Gap

No organized Arabic catalog for Kafaat/Edafaa custom modules; mixed hardcoding; remaining English menus/forms.

## 4. Proposed implementation

1. **Lock scope** with client: SIS/edafaa only vs full OpenEduCat + Motakamel  
2. Export / create `i18n/ar_001.po` for each edafaa module  
3. Replace hardcoded Arabic with English source + Arabic translations  
4. UAT: set user language to `ar_001`, walk student / registration / batch / courses  
5. Attach coverage report  

**Modules:** all `edafaa_*` + optionally `student_enrollment_portal`

## 5. Acceptance criteria

- [ ] Agreed scope listed on WP  
- [ ] Critical flows Arabic when lang = ar_001  
- [ ] No mixed EN/AR on in-scope screens  
- [ ] Coverage report attached  

## 6. Open questions

1. Scope: SIS only or entire Odoo education stack?  
2. Default language for all Kafaat users = Arabic?

## 7. Risks

High effort; easy to under-estimate if “full UI” includes accounting, HR, CRM. Must lock scope first.
