# Training Program & CRM Enhancements — Master Plan

**Project:** Kafaat / Edafaa Odoo 19  
**Repository:** `/opt/new_kafaat`  
**Base branch:** `feature/student-profile-p1-crs-code`  
**Working branch:** `feature/training-program-crm-enhancements`  
**Runtime addons path:** `/opt/localaddons` (Odoo loads from here — sync git → localaddons before upgrade)  
**Test database:** `sabry-test`  
**Odoo URL:** `http://localhost:8069`  
**Plan date:** 2026-06-07

---

## Scope

1. **CRM improvements** — Sales Team monthly target based on lead count; targeted Students wording in CRM; student contact → `op.student` visibility bridge.
2. **Program workflow** — Controlled `state` lifecycle on `op.program` (Draft → Under Review → Approved → Published → Archived).
3. **Program tabs & Arabic labels** — Structured notebook pages on program form with client-requested Arabic section titles.
4. **Program fields** — Duration, training language, max trainees, schedules, objectives, career outcomes.
5. **Marketing & course linkage** — Brochure/materials fields; linked `op.course` list and smart button on program.
6. **Regression** — Prior Student Profile P1 features remain functional.
7. **UAT** — Playwright scenarios, screenshots, structured reports.
8. **Final delivery report** — Executive summary and readiness assessment.

### Implementation module

New addon: **`edafaa_training_crm`** in `custom_addons/`, depending on `edafaa_student_profile`, `crm`, `sale`, `openeducat_core`.  
Does **not** modify finished Student Profile logic except integration touchpoints (program form inherit order, partner→student bridge).

---

## Out of scope

- Global rename of all "Customer" / "Contact" labels across Accounting, Sales Orders, or Invoicing.
- Porting full `motakamel.program` sub-models (accreditation, pricing, delivery as separate tables) — use lightweight text/HTML fields on `op.program` instead.
- Website/public enrollment availability changes (Published state is workflow/UI only unless future website module consumes it).
- Replacing `motakamel.program` or `gr.training.program` as canonical training catalog.
- Docker/deployment infrastructure changes.
- Committing credentials, `.env`, Playwright auth state, `node_modules`, videos, or large traces.

---

## Phases

| Phase | Goal | Deliverables | Commit message |
|-------|------|--------------|----------------|
| **0** | Investigation & gap analysis | `PHASE_0_GAP_ANALYSIS.md` | `[training-crm] Phase 0: gap analysis and master plan` |
| **1** | CRM improvements | Code, tests, `PHASE_1_*` docs | `[training-crm] Phase 1: CRM student and lead target improvements` |
| **2** | Program workflow/stages | Code, tests, `PHASE_2_*` docs | `[training-crm] Phase 2: program workflow stages` |
| **3** | Program tabs & Arabic labels | Views, tests, `PHASE_3_*` docs | `[training-crm] Phase 3: program tabs and Arabic labels` |
| **4** | Program enhancement fields | Model fields, tests, `PHASE_4_*` docs | `[training-crm] Phase 4: program enhancement fields` |
| **5** | Marketing & course linkage | Views, tests, `PHASE_5_*` docs | `[training-crm] Phase 5: program marketing and course linkage` |
| **6** | Full regression | Module upgrade, `PHASE_6_REGRESSION_TEST_RESULT.md` | `[training-crm] Phase 6: regression validation` |
| **7** | Playwright UAT | `training_crm_uat.spec.ts`, screenshots, `PLAYWRIGHT_UAT_REPORT.md` | `[training-crm] Phase 7: Playwright UAT evidence` |
| **8** | Final summary | `FINAL_COMPLETION_REPORT.md` | `[training-crm] Phase 8: final completion report` |
| **9** | Push | Clean tree, push branch | (no separate commit if docs in phase 8) |

---

## Acceptance criteria

### Phase 1 — CRM
- [ ] `crm.team` has `lead_target` (integer, monthly lead count goal).
- [ ] Team form/dashboard shows lead-based target (not only invoicing target in CRM context).
- [ ] CRM "Customers" menu relabeled "Students" (CRM scope only).
- [ ] Partner with `is_student=True` and sufficient profile data auto-creates or links `op.student`; appears in Students menu.

### Phase 2 — Workflow
- [ ] `op.program.state` with five stages and Arabic-friendly labels.
- [ ] Header statusbar and transition buttons (Submit, Approve, Publish, Archive, Reset to Draft).
- [ ] Existing programs default to `draft`; creation not blocked.

### Phase 3 — Tabs
- [ ] Program form notebook pages with Arabic titles: وصف البرنامج، الاعتمادات والشهادات، الفئة المستهدفة، طريقة التقديم، التسعير والرسوم، متطلبات الالتحاق، التسويق والإعلان، الإدارة الداخلية.
- [ ] Skills tab from `edafaa_student_profile` preserved.

### Phase 4 — Fields
- [ ] Duration, training language, max trainees, schedules, objectives, outcomes on program form in appropriate tabs.
- [ ] No required constraints blocking legacy program records.

### Phase 5 — Marketing & courses
- [ ] Linked courses visible (One2many from `op.course.program_id`).
- [ ] Marketing brochure/materials fields on program.
- [ ] Course count smart button or inline list.

### Phase 6 — Regression
- [ ] Module upgrade on `sabry-test` without view errors.
- [ ] Student profile, Courses tab, Skills, Certificates still open.

### Phase 7 — Playwright
- [ ] All UAT scenarios executed with PASS/FAIL/SKIPPED/BLOCKED status.
- [ ] Screenshots `01`–`09` captured under `uat_evidence/screenshots/`.

---

## Test strategy

| Layer | Tool | When |
|-------|------|------|
| Unit / ORM | Odoo `TransactionCase` in `edafaa_training_crm/tests/` | After phases 1–5 |
| Module upgrade | `odoo -u edafaa_training_crm --test-enable --stop-after-init` | Phase 6 |
| UI / UAT | Playwright headless against `localhost:8069` | Phase 7 |
| Manual smoke | Odoo backend form open via RPC/action IDs | Phase 6 |

Credentials via environment variables only (`ODOO_PASSWORD`); never committed.

---

## Screenshot strategy

- Directory: `docs/training_crm_enhancements/uat_evidence/screenshots/`
- Naming: `01_crm_lead_target.png` … `09_student_profile_regression.png`
- Full-page screenshots after modal dismissal (G2 promo popup pattern from Student Profile UAT).
- Playwright report links relative paths from `uat_evidence/reports/PLAYWRIGHT_UAT_REPORT.md`.

---

## Commit strategy

- One commit per completed phase (code + phase docs together).
- Phase 7 may include screenshot binaries + report (no credentials).
- Phase 8 final report may be separate commit or combined with Phase 7 evidence.
- Push once all commits are clean and `git status` shows no unintended untracked secrets.

---

## Known risks

| Risk | Mitigation |
|------|------------|
| Git vs runtime drift (`/opt/new_kafaat` vs `/opt/localaddons`) | `rsync` `edafaa_*` modules before upgrade |
| `edafaa_student_profile` security CSV drift in runtime | Verify `ir.model.access.csv` before upgrade |
| Required student fields block auto-create from contact | Bridge only when partner has minimum data; document assumption |
| Global Customer rename breaks Accounting | CRM-menu-only relabel |
| `op.program` vs `motakamel.program` parallel stacks | Extend `op.program` only; document motakamel as reference |
| Playwright save unreliable | RPC create + UI verify pattern from Student Profile |
| Published state ≠ website enrollment | Document as workflow-only |

---

## Final report path

`docs/training_crm_enhancements/FINAL_COMPLETION_REPORT.md`

Supporting artifacts:

- `docs/training_crm_enhancements/PHASE_*_*.md`
- `docs/training_crm_enhancements/uat_evidence/reports/PLAYWRIGHT_UAT_REPORT.md`
- `docs/training_crm_enhancements/uat_evidence/screenshots/*.png`
