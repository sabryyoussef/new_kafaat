# OP#86 — Implementation Report

**Date:** 2026-07-01  
**Branch:** `feature/op86-kafaat-trainee-request`  
**Database validated:** `sabry-test`

## Summary

Implemented trainee field binding fixes, UI cleanup, certificate search filters, and multi-select batch assignment per the OP#86 plan. Primary work lives in `edafaa_student_profile` with bridge modules for portal, admission, batch intake, and CRM partner sync.

## Phases

| Phase | Status | Key deliverables |
|-------|--------|------------------|
| 0 Discovery | Done | [`PHASE_0_DISCOVERY.md`](PHASE_0_DISCOVERY.md) |
| 1 Field bindings | Done | Address, phone, ID sync; `specialization_id` → `op.program` |
| 2 UI cleanup | Done | Trainee form uses `id_number`; hidden cert columns, Documents tab, partner ID |
| 3 Certificate filters | Done | Search filters + group-by on `op.student` |
| 4 Batch wizard | Done | `batch.trainee.assignment.wizard` on multi-select list |
| 5 Verification | Done | 7 unit tests green; UAT checklist + Playwright scaffold |

## Modules changed

| Module | Version | Changes |
|--------|---------|---------|
| `edafaa_student_profile` | 19.0.2.0.0 | `specialization_id`, cert search fields, partner sync, admission inherit, views, tests |
| `edafaa_student_profile_portal` | — | Map specialization + cert fields; hide Documents page |
| `edafaa_training_crm` | 19.0.1.1.0 | Partner ID uses `id_number` only; hide partner ID on contact form |
| `admission_integration` | — | Fix nationality/address conflation; admission vals include ID/address/specialization |
| `edafaa_batch_intake` | 19.0.2.0.0 | CSV profile enrichment, batch assignment wizard, security |
| `batch_intake` | — | Copied to git (installed on sabry-test) |

## Field binding fixes

| Field | Canonical | Sync paths fixed |
|-------|-----------|------------------|
| العنوان | Partner address | Registration portal, admission enroll, batch CSV, admission_integration |
| رقم الهاتف | Partner `phone` | Student create/write sync; admission `mobile` → `phone` |
| رقم الهوية | `op.student.id_number` | Student ↔ partner sync; CRM no vat/ref fallback |
| التخصص | `specialization_id` → `op.program` | Registration, admission, student form |

## Tests

```bash
cp -a custom_addons/edafaa_* custom_addons/batch_intake custom_addons/admission_integration /opt/localaddons/
odoo -c /etc/odoo/odoo.conf -d sabry-test \
  -u edafaa_student_profile,edafaa_batch_intake \
  --test-enable --stop-after-init \
  --test-tags=/edafaa_student_profile,/edafaa_batch_intake \
  --http-port=8079
```

**Result (2026-07-01):** 7 tests, 0 failed, 0 errors.

| Test | Module |
|------|--------|
| `test_student_syncs_id_and_phone_to_partner` | edafaa_student_profile |
| `test_admission_enroll_maps_id_and_mobile` | edafaa_student_profile |
| `test_specialization_stored_on_student` | edafaa_student_profile |
| `test_batch_intake_row_extract` | edafaa_batch_intake |
| `test_process_blocked_without_schedule_batch` | edafaa_batch_intake |
| `test_partner_sync_on_student_intake_write` | edafaa_batch_intake |
| `test_edafaa_batch_intake_menu_exists` | edafaa_batch_intake |

## Upgrade command (full stack)

```bash
odoo -c /etc/odoo/odoo.conf -d sabry-test \
  -u edafaa_training_crm,edafaa_student_profile,edafaa_student_profile_portal,\
edafaa_batch_intake,batch_intake,admission_integration \
  --stop-after-init --http-port=8079
```

## Playwright

Scaffold: [`tests/playwright/op86/`](/opt/new_kafaat/tests/playwright/op86/) — run against staging with `ODOO_URL`, `ODOO_USER`, `ODOO_PASSWORD`.

## Notes

- Do **not** install `batch_intake_processor` alongside `batch_intake`.
- Avoid circular manifest dependency between `edafaa_student_profile` and `edafaa_training_crm`; partner ID UI fix is in training CRM module.
- Client staging UAT required before production.
