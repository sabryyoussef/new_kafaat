# Student Profile — Playwright UAT

Browser-based UAT screenshots for `edafaa_student_profile` delivery validation.

## Prerequisites

- Odoo running and reachable (default `http://localhost:8069`)
- Database `sabry-test` with modules installed:
  - `edafaa_student_profile`
  - `edafaa_student_profile_portal` (for UAT-04)
- UAT fixtures seeded on `sabry-test` before run (students `UAT-PW-A` / `UAT-PW-B`, parent link, enrollments, issued certificate). Seed script must `env.cr.commit()` and set both `op.parent.student_ids` and `op.student.parent_ids`.

## Environment variables (required)

```bash
export ODOO_BASE_URL="http://localhost:8069"
export ODOO_DB="sabry-test"
export ODOO_LOGIN="admin"
export ODOO_PASSWORD="***"   # do not commit
```

## Install and run

```bash
cd tests/playwright/student_profile
npm install
npx playwright install chromium
npm test
```

Screenshots are written to:

`docs/student_profile/uat_evidence/screenshots/`

## Do not commit

- `.auth/`
- `.env`
- `node_modules/`
- credentials or trace files
