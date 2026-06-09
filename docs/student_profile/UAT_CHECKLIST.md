# Student Profile — UAT Checklist

**Project:** Kafaat / Edafaa — OpenEduCat SIS  
**Branch:** `feature/student-profile-p1-crs-code`  
**Addon:** `edafaa_student_profile` (+ `edafaa_student_profile_portal` for Step 3B)  
**Test database:** `sabry-test` (or target UAT DB after module upgrade)

---

## Pre-UAT setup

- [ ] Upgrade addons on target DB:
  ```bash
  odoo -c /etc/odoo/odoo.conf -d <UAT_DB> -u edafaa_student_profile,edafaa_student_profile_portal --stop-after-init
  ```
- [ ] Confirm runtime addons synced:
  - `/opt/localaddons/edafaa_student_profile`
  - `/opt/localaddons/edafaa_student_profile_portal` (if portal bridge used)
- [ ] Log in as **OpenEduCat Back Office Admin** (or equivalent editor role)

---

## 1. Course code (CRS-XXXX)

| # | Test | Steps | Expected | Pass |
|---|------|-------|----------|------|
| 1.1 | Auto code on create | OpenEduCat → Configuration → Course Management → Courses → Create; leave **Code** empty; save | Code auto-filled `CRS-0001` (or next sequence) | ☐ |
| 1.2 | Manual code preserved | Create course with code `CUSTOM-CRS-01`; save | Code remains `CUSTOM-CRS-01` | ☐ |

---

## 2. Program code (PRG-XXXX)

| # | Test | Steps | Expected | Pass |
|---|------|-------|----------|------|
| 2.1 | Auto code on create | Configuration → Programs → Create; leave **Code** empty; save | Code auto-filled `PRG-0001` (or next sequence) | ☐ |
| 2.2 | Manual code preserved | Create program with code `CUSTOM-PRG-01`; save | Code remains `CUSTOM-PRG-01` | ☐ |

**Note:** `motakamel.program` uses a different model/sequence — not in scope.

---

## 3. Student required fields

| # | Test | Steps | Expected | Pass |
|---|------|-------|----------|------|
| 3.1 | Arabic name required | Create student without **Arabic Name** | Validation error / cannot save | ☐ |
| 3.2 | English name required | Create without **English Name** | Validation error | ☐ |
| 3.3 | ID required | Create without **ID Number** | Validation error | ☐ |
| 3.4 | Email required | Create without **Email** | Validation error | ☐ |
| 3.5 | Phone required | Create without **Phone** | Validation error | ☐ |
| 3.6 | Birth date required | Create without **Birth Date** | Validation error | ☐ |
| 3.7 | Address required | Create without **Street**, **City**, or **Country** | Validation error | ☐ |
| 3.8 | English name on certificate/report | Set English name; save; open student | `name` / reports use English full name | ☐ |

---

## 4. Portal registration bridge (Step 3B)

**Requires:** `edafaa_student_profile_portal` installed; staff registration workflow active.

| # | Test | Steps | Expected | Pass |
|---|------|-------|----------|------|
| 4.1 | Staff captures ID/address | Open portal registration; fill ID + address fields on staff form | Fields saved on registration record | ☐ |
| 4.2 | Approval creates `op.student` | Approve registration | `op.student` created with mapped profile fields | ☐ |
| 4.3 | Bilingual names map | Registration has Arabic + English names | `name_arabic`, `name_english` correct on `op.student` | ☐ |

**Known divergence:** Git repo portal may target `gr.student`; runtime bridge maps to `op.student` — document environment used for UAT.

---

## 5. Family and siblings

| # | Test | Steps | Expected | Pass |
|---|------|-------|----------|------|
| 5.1 | Link shared parent | Create/link same parent on two students | Both show parent in **Family** tab | ☐ |
| 5.2 | Sibling visibility | Open Student A | **Siblings** lists Student B | ☐ |
| 5.3 | Reciprocal sibling | Open Student B | **Siblings** lists Student A | ☐ |
| 5.4 | Self excluded | Open either student | Student does **not** appear in own siblings list | ☐ |

---

## 6. Training summary

| # | Test | Steps | Expected | Pass |
|---|------|-------|----------|------|
| 6.1 | No enrollment | Student with zero `op.student.course` rows | **Training Status** = New Trainee | ☐ |
| 6.2 | Running enrollment | Add enrollment `state=running` | **Currently Registered**; current course/batch shown | ☐ |
| 6.3 | Finished only | Only `state=finished` enrollments | **Completed** | ☐ |
| 6.4 | Counts | Mix running + finished | Running/Completed counts correct | ☐ |

---

## 7. Courses tab

| # | Test | Steps | Expected | Pass |
|---|------|-------|----------|------|
| 7.1 | Tab visible | Open student form | **Courses** tab present (after Family) | ☐ |
| 7.2 | Enrollment rows | Student with enrollments | Course, batch, roll number, status visible | ☐ |
| 7.3 | Running row | One `running` enrollment | Badge shows running | ☐ |
| 7.4 | Finished row | One `finished` enrollment | Badge shows finished | ☐ |
| 7.5 | Readonly | Try inline create/edit on list | No create/edit/delete on tab (readonly) | ☐ |

---

## 8. Skills (course and program)

| # | Test | Steps | Expected | Pass |
|---|------|-------|----------|------|
| 8.1 | Create skill | Configuration → Course Management → **Skills** (or inline) | `edafaa.skill` record saved | ☐ |
| 8.2 | Course Skills tab | Open course form | **Skills** tab after **Subjects** | ☐ |
| 8.3 | Assign to course | Add skills on course; save/reload | Skills persist | ☐ |
| 8.4 | Subjects unchanged | Open course **Subjects** tab | `subject_ids` unchanged; label still **Subjects** | ☐ |
| 8.5 | Program Skills tab | Open program form | Notebook with **Skills** tab | ☐ |
| 8.6 | Assign to program | Add skills on program; save/reload | Skills persist | ☐ |

**MVP:** Skills are tag/catalog only — no skill levels.

---

## 9. Certificate workflow

| # | Test | Steps | Expected | Pass |
|---|------|-------|----------|------|
| 9.1 | Issue for finished | Student with `finished` enrollment → **Issue Certificate** on Courses tab | Certificate created; state **Issued** | ☐ |
| 9.2 | Block running | Try issue on `running` enrollment | Blocked (no button or validation error) | ☐ |
| 9.3 | Certificate number | After issue | Number format `CERT-YYYY-XXXX` | ☐ |
| 9.4 | PDF generated | Open certificate record | PDF attachment present | ☐ |
| 9.5 | Courses tab display | Finished row | Certificate number / actions visible | ☐ |
| 9.6 | Download | Click **Download** | PDF opens/downloads | ☐ |
| 9.7 | Email validation | Student without email → **Send Email** | Clear validation error | ☐ |
| 9.8 | Email action | Student with email → **Send Email** | `mail.mail` created; cert state **Sent** | ☐ |
| 9.9 | Bonafide unchanged | Print bonafide wizard | Still uses `CERT/` sequence on `op.student.certificate_number` | ☐ |

---

## 10. Known UAT limitations

| Item | Notes |
|------|-------|
| **SMTP** | Real email delivery requires outgoing mail server on UAT/production. Test may only verify `mail.mail` record creation. |
| **PDF branding** | Completion certificate uses minimal QWeb template — client design approval / polish deferred. |
| **Portal certificate download** | Not included in Steps 1–8. Grants portal download remains stubbed (`href="#"`). |
| **Runtime vs git portal** | Step 3B bridge targets runtime `op.student`; git `student_enrollment_portal` may differ — document UAT environment. |
| **`gr.certificate`** | Not modified; separate grants stack on `gr.student`. |

---

## UAT sign-off

| Role | Name | Date | Result |
|------|------|------|--------|
| QA / UAT | | | ☐ Pass ☐ Fail |
| Product owner | | | ☐ Approved ☐ Changes requested |
| Technical lead | | | ☐ Approved |

**Comments:**

---

## Reference commits (local)

| Step | Commit |
|------|--------|
| 1 | `937ee172` |
| 2 | `74c304f5` |
| 3 | `9b20b3be` |
| 3B | `6463d825` |
| 4 | `fffa46bf` |
| 5 | `ed21f04` |
| 6 | `e197e158` |
| 7 | `ec853751` |
| 8 | `9416fd9` |
