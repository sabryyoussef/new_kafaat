# OP#206 — UAT Retest Checklist

**Environment:** Client staging after upgrade of `edafaa_student_profile` 19.0.2.1.0  
**Reference:** [OP206_UAT_FIX_REPORT.md](OP206_UAT_FIX_REPORT.md)

## Pre-flight

- [ ] Modules upgraded: `edafaa_student_profile`, `edafaa_student_profile_portal`, `edafaa_batch_intake`
- [ ] Odoo workers reloaded

## 1. Group By Current Course

- [ ] Open SIS → Students
- [ ] Open Group By menu
- [ ] **المقرر الحالي** / Current Course is listed
- [ ] Selecting it groups trainees by current course

## 2. Labels and mapping

- [ ] Open a trainee created from Student Registration
- [ ] Labels show: رقم الهوية، رقم الهاتف، التخصص، الشارع، المدينة، الدولة
- [ ] Values match the registration record

## 3. Blood Group hidden

- [ ] Blood Group not on trainee form
- [ ] Blood Group not on student list columns
- [ ] Blood Group not in search Group By

## 4. Registration Number and Source Type

- [ ] Create/finalize a Student Registration
- [ ] Open resulting Student Profile
- [ ] **رقم التسجيل** equals registration number (e.g. REG000xx)
- [ ] **نوع المصدر** = Student Registration Portal

## Sign-off

| Role | Name | Date | Pass/Fail |
|------|------|------|-----------|
| Kafaat admin | | | |
| Edafaa dev | | | |
