# Requirement Analysis — OP#352 / Odoo #43

**Subject:** Student application status on profile (`حالة الطالب`)  
**Priority:** High  
**Status:** **PARTIAL** (adjacent workflows exist; required 4 values not on profile)  
**Estimate:** 2–3 days  
**Links:** [OP#352](https://master.tailcf9988.ts.net:10081/work_packages/352) · [Odoo #43](http://127.0.0.1:8069/web#id=43&model=project.task&view_type=form&db=sabry-test)

---

## 1. Client requirement

Add **student status** on the student profile with:

| Arabic | Suggested technical value |
|--------|---------------------------|
| مقبول | `accepted` |
| مرفوض | `rejected` |
| تحت المراجعة | `under_review` |
| ملغي | `cancelled` |

## 2. Current system

| Model | Field | Values | Match? |
|-------|-------|--------|--------|
| `op.student` | `training_status` | new / active / completed | No — training lifecycle |
| `student.registration` | `state` | draft, submitted, eligibility_review, document_review, approved, rejected, enrolled | Partial — no ملغي; not on profile |
| `op.admission` | `state` | draft, submit, confirm, reject, cancel, done | On admission, not student profile |

### Evidence

- `edafaa_student_profile/models/student.py` — `training_status`
- `student_enrollment_portal/models/student_registration.py` — registration workflow
- No `application_status` (or equivalent) on `op.student`

## 3. Gap

Client wants a **single visible status on ملف الطالب** with four labels. Existing fields either mean something else (`training_status`) or live only on registration (portal), not the SIS profile form.

## 4. Proposed implementation

1. **Decide with client:** stored field on `op.student` vs related from latest registration  
2. Add Selection `application_status` on `op.student` with Arabic `string` / selection labels  
3. Map from registration finalize / admission reject|cancel where possible  
4. Show on form, list, optional search / group-by  
5. Document mapping table for ops  

**Recommended default:** Field on `op.student` + sync from registration when present.

**Module:** `edafaa_student_profile` (+ portal bridge if sync from registration)

## 5. Acceptance criteria

- [ ] Four statuses available on student profile (Arabic)
- [ ] Visible on form and list
- [ ] Mapping from registration/admission documented
- [ ] UAT on staging

## 6. Open questions

1. Does status apply to SIS `op.student` only, or also show on portal registration?
2. Who can change status manually after enrollment?
3. Should ملغي archive the student (`active=False`)?

## 7. Risks

Medium — confusing with `training_status` if both shown without clear labels. Need UX decision before coding.
