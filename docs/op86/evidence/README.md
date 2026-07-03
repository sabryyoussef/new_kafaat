# OP#86 Playwright evidence

**Captured:** 2026-07-01 on `sabry-test`  
**Path:** `docs/op86/evidence/screenshots/`

| File | Screen |
|------|--------|
| `00_home_apps.png` | Odoo app switcher (login) |
| `01_student_list.png` | SIS → Students kanban |
| `02_student_list_filters.png` | Student search / filters |
| `03_trainee_form.png` | Trainee profile (`op.student`) |
| `04b_registration_list.png` | Student Registrations kanban |
| `04_registration_form.png` | Registration form with OP86 fields |
| `05_student_multi_select.png` | Student list multi-select |

## Run tests

```bash
cd tests/playwright/op86
npm install
npx playwright install chromium
ODOO_PASSWORD=admin npm test
```

## Capture all screenshots (no assertions)

```bash
ODOO_PASSWORD=admin npm run screenshots
```

## Note

Student list was broken until `student_search_views.xml` stopped declaring `specialization_id` as a search `<field>` (filters/group-by only). Upgrade `edafaa_student_profile` and reload Odoo after pulling.
