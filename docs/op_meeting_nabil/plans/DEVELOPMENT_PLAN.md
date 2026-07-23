# Kafaat Meeting Requirements — Development Plan

**Version:** 1.1  
**Date:** 2026-07-15  
**Source:** nabil@kafaat.edu.sa meeting (2026-07-07)  
**OpenProject:** #351–#358 under parent #87  
**Odoo:** parent #41, children #42–#49 (`sabry-test`)  
**Branches:** S1 `feature/meeting-s1-351-353-356` · S2 `feature/meeting-s2-352-354` · S3 `feature/meeting-s3-355` · S5 `feature/meeting-s5-358`

---

## 1. Timeline overview

| Sprint | Days | Focus | OP WPs | Effort | Status |
|--------|------|-------|--------|--------|--------|
| **S1** | 1–2 | Quick wins + investigate | #351, #353, #356 | ~1.5–2 d | **Done** (2026-07-15, `feature/meeting-s1-351-353-356`) |
| **S2** | 3–6 | Profile fields + Batch guide | #352, #354 | ~3.5–5 d | **Done** (2026-07-15, `feature/meeting-s2-352-354`) |
| **S3** | 7–14 | Excel sales assignment | #355 | ~5–7 d | **Done** (2026-07-15, `feature/meeting-s3-355`) |
| **S4** | 15–30+ | Arabic i18n (scoped) | #357 | ~2–4 w | Pending (plan locked Scope A) |
| **S5** | parallel / after S4 | Batch QR attendance | #358 | ~3–5 w | **Done** (2026-07-15, `feature/meeting-s5-358`) |

### S1 locked delivery (2026-07-15 recreate)

| WP | Work | Outcome |
|----|------|---------|
| #351 | Search `id_number` + `_rec_names_search` | Code |
| #353 | `voucher_number` on profile (manual) | Code |
| #356 | Courses visibility findings (no ACL change) | Docs |

Order: #351 → #353 → #356 → upgrade/UAT sabry-test → OP/Odoo close.

### S2 locked delivery (2026-07-15 recreate)

| WP | Work | Outcome |
|----|------|---------|
| #352 | `application_status` on profile + registration sync | Code |
| #354 | Batch Arabic user guide + screenshots | Docs |

Locked: field on `op.student` (not `training_status`); ملغي does not archive; #354 docs-only (CSV only / no xlsx).  
Order: #352 → #354 → upgrade/UAT → Playwright → OP/Odoo delivery + close.

### S3 locked delivery (2026-07-15 recreate)

| WP | Work | Outcome |
|----|------|---------|
| #355 | Excel bulk assign trainees → `assigned_user_id` (sales user) | Code |

Locked: match by `id_number`; staff by login/email; overwrite; `.xlsx` + reject CSV; SIS only (not CRM/grants).  
Order: field → wizard → tests/PW → delivery + close.

### S5 locked delivery (2026-07-15)

| WP | Work | Outcome |
|----|------|---------|
| #358 | Stable QR per batch + portal check-in → OpenEduCat attendance | Code |

Locked: **1A portal** (phone); **stable QR** (regenerate revokes); late after **15 min** grace; enrollment `running` required.  
Module: `edafaa_batch_attendance`. Out: kiosk, daily QR.

**Calendar (1 FTE developer):**

| Week | Work |
|------|------|
| Week 1 | S1 complete + start #352 |
| Week 2 | Finish #352 + #354 |
| Week 3–4 | #355 Excel sales |
| Week 5–8 | #357 Arabic (SIS scope) |
| Week 9–14 | #358 QR attendance (after design sign-off) |

**Total core (S1–S3):** ~10–14 developer-days  
**With translation + QR (S4–S5):** ~6–12 additional weeks

---

## 2. Delivery order (locked)

```
S1: #351 Search ID → #356 Courses investigate → #353 Voucher
S2: #352 Application status → #354 Batch Arabic guide
S3: #355 Excel → sales
S4: #357 Arabic UI (scope lock first)
S5: #358 Batch QR (design lock first)
```

---

## 3. Environments

| Step | DB |
|------|-----|
| Dev / UAT | `sabry-test` |
| Client verify | `TR_K19` |
| Sync | Implement in `/opt/new_kafaat/custom_addons` → deploy to `/opt/localaddons` |

Standard upgrade:

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test \
  -u edafaa_student_profile,edafaa_student_profile_portal,edafaa_batch_intake,edafaa_training_crm \
  --stop-after-init
```

---

## 4. Per-WP plans (index)

| WP | Plan file | Days |
|----|-----------|------|
| #351 | [PLAN_WP351.md](PLAN_WP351.md) | 0.5 |
| #352 | [PLAN_WP352.md](PLAN_WP352.md) | 2–3 |
| #353 | [PLAN_WP353.md](PLAN_WP353.md) | 0.5 |
| #354 | [PLAN_WP354.md](PLAN_WP354.md) | 1–2 |
| #355 | [PLAN_WP355.md](PLAN_WP355.md) | 5–7 |
| #356 | [PLAN_WP356.md](PLAN_WP356.md) | 0.5–1 |
| #357 | [PLAN_WP357.md](PLAN_WP357.md) | 2–4 w |
| #358 | [IMPLEMENTATION_PLAN_S5_WP358.md](IMPLEMENTATION_PLAN_S5_WP358.md) | 3–6 w |

Analysis docs: [`../analysis/`](../analysis/)

---

## 5. Definition of Done (all WPs)

- [ ] Code / docs merged to feature branch  
- [ ] Unit or shell tests on `sabry-test`  
- [ ] UAT checklist checked on WP  
- [ ] Comment posted on OpenProject + Odoo task  
- [ ] Deployed to TR_K19 when client-ready  

---

## 6. Risks & blockers

| Risk | Mitigation |
|------|------------|
| #352 status vs training_status confusion | Separate badges; mapping doc in PLAN_WP352 |
| #355 Excel columns unknown | Template workshop before S3 |
| #357 “full UI” scope creep | Lock SIS-only scope in writing |
| #358 portal vs kiosk | Design WP / comment before any code |
| Excel in batch_intake already broken for xlsx | Document in #354; separate WP if client wants .xlsx parse |

---

## 7. Team / roles

| Role | Owner |
|------|-------|
| Dev | — |
| UAT on Kafaat | Client + Edafaa QA |
| OP / Odoo status updates | Dev after each WP |
