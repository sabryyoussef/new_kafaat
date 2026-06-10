# Phase 0 — Gap Analysis

**Date:** 2026-06-07  
**Database:** `sabry-test`  
**Runtime addons:** `/opt/localaddons`  
**Git addons:** `/opt/new_kafaat/custom_addons`  
**Config:** `/etc/odoo/odoo.conf` → `addons_path = .../odoo/addons,/opt/localaddons`

---

## Executive summary

The environment has **three parallel program/training stacks** and **two student stacks**. Student Profile P1 work correctly targets **`op.student`** / **`op.program`** via `edafaa_student_profile`. New CRM and program requirements should extend the same SIS models through a new addon **`edafaa_training_crm`**, using **`motakamel.program`** (localaddons only) as a **reference** for workflow and tab structure — not as the implementation target.

---

## What already exists

### CRM / Sales

| Area | Location | Status |
|------|----------|--------|
| `crm.team` base | Odoo `crm` + `sales_team` | Standard teams, assignment capacity, no custom lead target field |
| `invoiced_target` | Odoo `sale` on `crm.team` | Revenue-based monthly target (not lead count) |
| `crm.lead` extensions | `grants_training_suite_v19` | Pool/activity tracking only |
| CRM "Customers" menu | `crm/views/crm_menu_views.xml` | Points to `base.action_partner_form` |
| Lead assignment stats | `crm.team` | `lead_all_assigned_month_count`, `assignment_max` (member capacity) |

### Students / Contacts

| Area | Location | Status |
|------|----------|--------|
| `op.student` | `openeducat_core` | Canonical SIS student; delegates `res.partner` |
| `is_student` on partner | `openeducat_core/student_portal.py` | Boolean flag on `res.partner` |
| Student Profile P1 | `edafaa_student_profile` | Required fields, training summary, courses, skills, certificates, PRG codes |
| Portal bridge | `edafaa_student_profile_portal` | Registration → `op.student` |
| Students menu | `openeducat_core/menu/student_menu.xml` | SIS → Students action on `op.student` |
| `gr.student` | `grants_training_suite_v19` | Parallel grants stack (not primary for this work) |

### Programs / Courses

| Area | Location | Status |
|------|----------|--------|
| `op.program` base | `openeducat_core` | name, code, unit loads, department, image — **no state, no training tabs** |
| `op.course.program_id` | `openeducat_core/models/course.py` | Many2one link course → program |
| `edafaa_student_profile` on program | PRG auto-code, Skills tab | Extends `op.program` only |
| `motakamel.program` | `/opt/localaddons/motakamel` (not in git) | Full lifecycle, pricing, accreditations, marketing tabs — **reference only** |
| `gr.training.program` | `grants_training_suite_v19` | Grants training catalog (separate stack) |

---

## What is missing

| Requirement | Gap |
|-------------|-----|
| Sales Team target = lead count | Only `invoiced_target` (revenue) exists; no `lead_target` |
| CRM "Customers" → "Students" | Menu still "Customers" → all partners |
| Student contact in Students list | `is_student` on partner does not auto-create `op.student` |
| Program workflow stages | `op.program` has no `state` field |
| Arabic program tabs | Base form is single sheet, no notebook sections |
| Program training fields | No duration, language, max trainees, schedules, objectives, outcomes |
| Marketing/media on program | Only `image_1920`; no brochure/materials |
| Linked courses on program | Inverse One2many not exposed on program form |
| UAT for new features | No Playwright spec yet under `training_crm_enhancements/` |

---

## Configuration / data only (no code required)

| Item | Notes |
|------|-------|
| Demo lead records for UAT | Can use existing CRM data or create via RPC in tests |
| Arabic UI language | Install/activate `ar_001` for full UI translation; tab labels can be hardcoded Arabic in views as client requested |
| Sales team `use_leads` | May need enabling per team for lead pipeline UAT |
| Program content population | Objectives, outcomes, accreditations text — client data entry after fields exist |
| `motakamel.program` records | Legacy data; no migration in this phase |

---

## What needs code

| Phase | Module | Changes |
|-------|--------|---------|
| 1 | `edafaa_training_crm` | `crm.team.lead_target`, lead count compute, CRM menu relabel, `res.partner` → `op.student` bridge |
| 2 | `edafaa_training_crm` | `op.program.state`, workflow actions, statusbar |
| 3 | `edafaa_training_crm` | Program form notebook with Arabic tab labels |
| 4 | `edafaa_training_crm` | New fields on `op.program` |
| 5 | `edafaa_training_crm` | `course_ids` One2many, marketing fields, smart buttons |
| 6–7 | tests + Playwright | Regression and UAT automation |

---

## What is risky

| Risk | Severity | Notes |
|------|----------|-------|
| Git/runtime drift | **High** | Odoo loads `/opt/localaddons` only; must sync before upgrade |
| `edafaa_student_profile` ACL drift | **Medium** | Runtime security CSV may lack certificate rows |
| Auto-create student from contact | **Medium** | `edafaa_student_profile` requires many fields; bridge needs minimum-data guard |
| Global Customer rename | **High** | Avoid; CRM-menu-only change |
| Published state vs enrollment | **Low** | Workflow label only unless website consumes state |
| Notebook inherit conflict with Skills tab | **Medium** | Inherit order: base → edafaa skills → edafaa_training_crm tabs |
| Parallel `motakamel.program` confusion | **Medium** | Document canonical model = `op.program` |

---

## Recommended implementation approach

1. **Create `edafaa_training_crm`** addon in git; sync to `/opt/localaddons` for testing.
2. **Extend `op.program`** (not motakamel) for phases 2–5; preserve Skills tab from `edafaa_student_profile`.
3. **CRM changes are scoped**: lead target field + CRM Students menu + partner bridge — no accounting label changes.
4. **Student bridge**: on `res.partner` create/write when `is_student=True`, create `op.student` if missing and partner supplies minimum required profile data (name, email, phone, address, birth date, ID — map from partner fields; document fallbacks).
5. **Workflow**: new `state` Selection with safe defaults (`draft`); buttons with `groups` appropriate for managers; `active=False` on archive.
6. **Tabs**: lightweight Html/Text fields per section (not full motakamel sub-models).
7. **Courses**: `course_ids = One2many('op.course', 'program_id')` + count smart button.
8. **Testing**: Odoo unit tests per phase; Playwright UAT in phase 7; regression includes Student Profile scenarios.

---

## Phase 0 decision log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Canonical program model | `op.program` | Aligns with SIS, edafaa_student_profile, `op.course.program_id` |
| Implementation vehicle | New `edafaa_training_crm` | Avoid rewriting finished student profile module |
| motakamel.program | Reference only | Not in git; different model; high migration risk |
| Customer → Student scope | CRM menu only | Prevents accounting/sales side effects |
| Published enrollment | UI workflow only | No website module change in scope |

---

## Phase 0 status

**COMPLETE** — Analysis documented. Implementation may proceed to Phase 1.
