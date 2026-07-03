# OP#86 — UAT Checklist

**Environment:** Client staging (after sync from `feature/op86-kafaat-trainee-request`)  
**Reference:** [`OP86_IMPLEMENTATION_REPORT.md`](OP86_IMPLEMENTATION_REPORT.md)

## Pre-flight

- [ ] Modules upgraded: `edafaa_student_profile`, `edafaa_student_profile_portal`, `edafaa_training_crm`, `batch_intake`, `edafaa_batch_intake`, `admission_integration`
- [ ] Log in as back-office admin

## Trainee profile (`op.student`)

- [ ] Open existing trainee — **ID number** matches registration source (not vat/ref)
- [ ] **Address** (street, city, country) populated when created from registration
- [ ] **Phone** matches registration / admission mobile
- [ ] **Specialization** (التخصص) shows selected program
- [ ] **Category** field hidden or de-emphasized on form
- [ ] Courses tab — no `certificate_number` column clutter
- [ ] Search filters: Has Previous Certificate, Has Issued Certificate
- [ ] Group by Certificate Type works

## Registration (`student.registration`)

- [ ] Specialization field visible and saved
- [ ] ID, address fields present in profile bridge group
- [ ] Documents tab hidden
- [ ] Finalize creates student with all four client fields correct

## Admission path

- [ ] Create admission with mobile (no phone) — enroll student — phone on trainee matches mobile
- [ ] Nationality not overwriting address country
- [ ] ID number copied to trainee

## Batch intake

- [ ] CSV with mobile, address, national_id, program columns — partner/student enriched after process
- [ ] Multi-select trainees → **Assign to Batch** action → pick course + batch → enrollments updated

## CRM contact

- [ ] Partner ID field hidden on contact form (canonical ID on trainee only)
- [ ] Auto-create student from CRM contact uses `id_number` only

## Sign-off

| Role | Name | Date | Pass/Fail |
|------|------|------|-----------|
| Kafaat admin | | | |
| Edafaa dev | | | |
