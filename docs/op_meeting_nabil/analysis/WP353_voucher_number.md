# Requirement Analysis — OP#353 / Odoo #44

**Subject:** Voucher Number (`رقم قسيمة الاختبار`) on student profile  
**Priority:** Normal  
**Status:** **NOT IMPLEMENTED**  
**Estimate:** 0.5 day  
**Links:** [OP#353](https://master.tailcf9988.ts.net:10081/work_packages/353) · [Odoo #44](http://127.0.0.1:8069/web#id=44&model=project.task&view_type=form&db=sabry-test)

---

## 1. Client requirement

Add **Voucher Number** (`رقم قسيمة الاختبار`) to the student profile.

## 2. Current system

No field matching `voucher_number`, `voucher`, or `قسيمة` on:

- `op.student`
- `student.registration`
- `op.admission`

Closest unrelated: `registration_number`, `gr_no`, `certificate_number`.

## 3. Gap

Wholly missing field and UI.

## 4. Proposed implementation

1. Add `voucher_number = fields.Char(string='رقم قسيمة الاختبار')` on `op.student`  
2. Place on form (Personal Info or Training Summary); list/search if requested  
3. Optional: capture on registration / batch intake if source file includes it  
4. Upgrade + UAT  

**Module:** `edafaa_student_profile`

## 5. Acceptance criteria

- [ ] Field visible and editable on student profile (Arabic label)
- [ ] Value persists and shows in list if required
- [ ] Entry/import path documented

## 6. Open questions

1. Manual entry only, or imported from excel/external exam system?
2. Unique constraint required?

## 7. Risks

Low. Simple Char field unless uniqueness / external sync is required.
