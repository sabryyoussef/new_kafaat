# OP#86 — Phase 0 Discovery

**Date:** 2026-06-16  
**Database:** `sabry-test`  
**Branch:** `feature/op86-kafaat-trainee-request`

## Installed modules (sabry-test)

| Module | State |
|--------|-------|
| `edafaa_student_profile` | installed |
| `edafaa_student_profile_portal` | installed |
| `student_enrollment_portal` | installed |
| `edafaa_training_crm` | installed |
| `batch_intake` | installed |
| `edafaa_batch_intake` | installed |
| `admission_integration` | installed |

## Primary screens

| Screen | Model | Menu |
|--------|-------|------|
| Trainee profile | `op.student` | SIS → Students |
| Application | `student.registration` | Enrollment portal workflow |

## Field source matrix (signed for implementation)

| Client field | Canonical storage | Correct source | Fix |
|--------------|-------------------|----------------|-----|
| الجنسية | `op.student.nationality` | Registration / admission nationality | Keep; fix admission path conflating nationality with address country |
| العنوان | Partner `street`, `city`, `country_id` | Registration address fields | Map on all create paths; admission uses registration `country_id` not nationality text |
| التخصص | `op.student.specialization_id` → `op.program` | Registration `specialization_id` | **New field** (Many2one program) |
| رقم الهاتف | Partner `phone` (delegated) | Registration `phone`; admission `phone` or `mobile` | Sync; admission enroll copies mobile |
| رقم الهوية | `op.student.id_number` | Registration `id_number` only | Single source; sync partner; no vat/ref fallback |

## Specialty decision

**التخصص** implemented as `specialization_id` Many2one → `op.program` (training program specialization).

## Certificate filter

Filter on `op.student` by prior certificate (`has_previous_certificate`, `certificate_type`) and issued completion (`has_issued_certificate`).

## Batch stack

Implementation targets `batch_intake` + `edafaa_batch_intake` (not `batch_intake_processor`).
