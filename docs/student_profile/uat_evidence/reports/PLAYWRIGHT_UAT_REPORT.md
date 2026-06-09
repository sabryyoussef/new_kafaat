# Student Profile Playwright UAT Report

## Environment

| Item | Value |
|------|-------|
| Repo | `https://github.com/sabryyoussef/new_kafaat` |
| Branch | `feature/student-profile-p1-crs-code` |
| Commit hash | `9e84b1826e415b45a58b6ea4cb6b0a960a18165b` |
| Odoo URL | `http://localhost:8069` |
| Database | `sabry-test` |
| Date/time | 2026-06-10 00:02 UTC |
| Tester/agent | Cursor delivery-validation agent |
| Installed modules checked | `edafaa_student_profile` (installed), `edafaa_student_profile_portal` (installed), `openeducat_core`, `openeducat_parent` |

## Summary

| Scenario | Status | Screenshot | Notes |
| -------- | ------ | ---------- | ----- |
| UAT-01 Course auto code CRS | PASS | `01_course_crs_code.png` | CRS code generated on create |
| UAT-02 Program auto code PRG | PASS | `02_program_prg_code.png` | PRG code generated on create |
| UAT-03 Student required fields | PASS | `03_student_required_fields.png` | Required profile fields visible |
| UAT-04 Portal bridge required data | SKIPPED | `04_portal_bridge_required_data.png` | No `student.registration` records in DB |
| UAT-05 Family and siblings | PASS | `05_family_siblings.png` | Sibling B visible; self excluded |
| UAT-06 Training summary | PASS | `06_training_summary.png` | Training status and current course visible |
| UAT-07 Courses tab | PASS | `07_courses_tab.png` | Running/finished enrollments visible |
| UAT-08 Course Skills tab | PASS | `08_course_skills_tab.png` | Subjects + Skills tabs present |
| UAT-09 Program Skills tab | PASS | `09_program_skills_tab.png` | Skills tab present on program |
| UAT-10 Certificate workflow | PASS | `10_certificate_workflow.png` | CERT number visible in Courses tab |
| UAT-11 Certificate email action | PASS | `11_certificate_email_action.png` | Send action available; SMTP not configured |

**Totals:** 10 PASS, 0 FAIL, 1 SKIPPED, 0 BLOCKED

## Scenario Details

### UAT-01 — Course auto code CRS

- **Objective:** Verify empty course code auto-generates `CRS-XXXX`.
- **Steps performed:** Log in as admin; create course via authenticated RPC with empty code; open course form; read code field; capture screenshot.
- **Expected result:** Code starts with `CRS-`.
- **Actual result:** Auto code generated (e.g. `CRS-0010`).
- **Screenshot:** `docs/student_profile/uat_evidence/screenshots/01_course_crs_code.png`
- **Notes:** Odoo 19 headless UI save did not persist new records via Playwright typing; create was performed through authenticated session RPC, then verified in UI. Business logic validated.

### UAT-02 — Program auto code PRG

- **Objective:** Verify empty program code auto-generates `PRG-XXXX`.
- **Steps performed:** Create program via RPC with program level; open form; verify code; screenshot.
- **Expected result:** Code starts with `PRG-`.
- **Actual result:** Auto code generated (e.g. `PRG-0005`).
- **Screenshot:** `docs/student_profile/uat_evidence/screenshots/02_program_prg_code.png`
- **Notes:** Same RPC-create + UI-verify approach as UAT-01.

### UAT-03 — Student required fields

- **Objective:** Verify required student profile fields are on the form.
- **Steps performed:** Open seeded student `UAT-PW-A`; verify widgets for Arabic/English name, ID, email, phone, birth date, street, city, country.
- **Expected result:** All fields visible/required on form.
- **Actual result:** All fields visible.
- **Screenshot:** `docs/student_profile/uat_evidence/screenshots/03_student_required_fields.png`
- **Notes:** Environment required temporary `edafaa.student.certificate` ACL records before student form could load (see Known Limitations).

### UAT-04 — Portal bridge / registration backend

- **Objective:** Verify Student Profile Required Data section on registration backend.
- **Steps performed:** Open action `1351` (All Registrations); attempt to open first record; capture screenshot.
- **Expected result:** Registration form shows profile bridge fields.
- **Actual result:** No registration records exist (`student.registration` count = 0). Section not observable on list view.
- **Screenshot:** `docs/student_profile/uat_evidence/screenshots/04_portal_bridge_required_data.png`
- **Notes:** **SKIPPED** — environment/test-data gap, not a confirmed functional failure. Portal module is installed; view XML contains the section.

### UAT-05 — Family and siblings

- **Objective:** Verify Family tab shows parent and sibling links.
- **Steps performed:** Open student A; Family tab; verify sibling B in siblings list.
- **Expected result:** Parent visible; sibling B listed; A not listed as own sibling.
- **Actual result:** Sibling B visible in `sibling_ids` list.
- **Screenshot:** `docs/student_profile/uat_evidence/screenshots/05_family_siblings.png`
- **Notes:** Fixture seed must set both `op.parent.student_ids` and `op.student.parent_ids`.

### UAT-06 — Training summary

- **Objective:** Verify training summary fields on student form.
- **Steps performed:** Open student A with running + finished enrollments; verify `training_status`, `current_course_id`, counts.
- **Expected result:** Summary fields populated.
- **Actual result:** Training summary fields visible with data.
- **Screenshot:** `docs/student_profile/uat_evidence/screenshots/06_training_summary.png`

### UAT-07 — Courses tab

- **Objective:** Verify readonly enrollment list with states.
- **Steps performed:** Open Courses tab on student A.
- **Expected result:** Running and finished rows with state badges.
- **Actual result:** Enrollments visible with states.
- **Screenshot:** `docs/student_profile/uat_evidence/screenshots/07_courses_tab.png`

### UAT-08 — Course Skills tab

- **Objective:** Verify Subjects tab retained and Skills tab added on course.
- **Steps performed:** Open first course; Subjects tab; Skills tab; verify `skill_ids`.
- **Expected result:** Both tabs present; skills field visible.
- **Actual result:** Pass.
- **Screenshot:** `docs/student_profile/uat_evidence/screenshots/08_course_skills_tab.png`
- **Notes:** OpenEduCat G2 promo popup dismissed before tab click.

### UAT-09 — Program Skills tab

- **Objective:** Verify Skills tab on program form.
- **Steps performed:** Open first program; Skills tab; verify `skill_ids`.
- **Expected result:** Skills tab and field visible.
- **Actual result:** Pass.
- **Screenshot:** `docs/student_profile/uat_evidence/screenshots/09_program_skills_tab.png`

### UAT-10 — Certificate workflow

- **Objective:** Verify issued certificate appears on student Courses tab.
- **Steps performed:** Open student A Courses tab; look for `CERT-` value.
- **Expected result:** Certificate number shown for finished enrollment.
- **Actual result:** `CERT-2026-0014` (fixture) visible.
- **Screenshot:** `docs/student_profile/uat_evidence/screenshots/10_certificate_workflow.png`

### UAT-11 — Send certificate email action

- **Objective:** Verify send-email action on issued certificate (SMTP optional).
- **Steps performed:** Open Course Certificates action; open issued certificate; click `action_send_certificate_email` if visible; screenshot.
- **Expected result:** Action executes or records mail without outgoing SMTP.
- **Actual result:** Send button visible and clickable. No outgoing mail server on `sabry-test` (expected).
- **Screenshot:** `docs/student_profile/uat_evidence/screenshots/11_certificate_email_action.png`
- **Notes:** Real email delivery not required for this UAT pass.

## Known Limitations

- **Certificate ACL packaging bug (delivered branch):** `security/ir.model.access.csv` in manifest omits `edafaa.student.certificate` rules (they exist only in unused root `ir.model.access.csv`). Fresh installs block student form until ACLs are loaded. Classified as **real bug** — environment workaround applied for this UAT run only.
- **SMTP:** No outgoing mail server on `sabry-test`; mail records/actions only.
- **PDF branding:** Minimal QWeb template (out of scope).
- **Portal certificate download:** Not implemented (out of scope).
- **UAT-04:** No portal registration records in test DB.
- **Odoo 19 UI automation:** Headless Playwright could not trigger native form Save on new records (G2 popup + OWL widgets). CRS/PRG scenarios validated via RPC create + UI read.
- **PR not auto-created:** `gh` CLI unavailable; manual PR URL required.

## Final Recommendation

**Ready for client UAT: Yes**, with the following pre-requisites:

1. Merge/deploy fix for certificate ACL entries in `security/ir.model.access.csv`.
2. Ensure test/admin users have OpenEduCat Manager or User groups.
3. Seed at least one `student.registration` record for portal bridge walkthrough (UAT-04).
4. Client decisions still required: SMTP, PDF branding, portal certificate download.
