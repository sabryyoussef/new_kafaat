# Requirement Analysis — OP#358 / Odoo #49

**Subject:** Batch attendance with QR code per batch  
**Priority:** Low  
**Status:** **NOT IMPLEMENTED**  
**Estimate:** 3–6 weeks  
**Links:** [OP#358](https://master.tailcf9988.ts.net:10081/work_packages/358) · [Odoo #49](http://127.0.0.1:8069/web#id=49&model=project.task&view_type=form&db=sabry-test)

---

## 1. Client requirement

1. Generate a unique **QR Code** per **Batch**  
2. Only students enrolled in that batch can register attendance via QR  
3. Attendance register based on batch enrollment list  

## 2. Current system

| Capability | State |
|------------|-------|
| `openeducat_attendance` | Manual attendance with `course_id` + `batch_id` |
| Staff take-attendance API | Exists — not student QR check-in |
| QR token on `op.batch` | **Missing** |
| Portal / kiosk scan | **Missing** |
| Enterprise attendance / barcode modules | Referenced in config, **not installed** |

## 3. Gap

All QR / enrollment-gated self-attendance acceptance criteria are unmet. Manual attendance is foundation only.

## 4. Proposed implementation (high level)

1. Design: student mobile portal vs classroom kiosk (client decision)  
2. `attendance_qr_token` on `op.batch` + QR print/download  
3. Controller/portal: scan → verify `op.student.course` enrollment for batch → create/update `op.attendance.line`  
4. Optional: auto-create `op.attendance.register` when batch starts  
5. Revocation, rate limits, audit log  
6. UAT scenarios  

**Suggested new module:** `edafaa_batch_attendance`

## 5. Acceptance criteria

- [ ] Each batch has unique scannable QR (revocable)  
- [ ] Non-enrolled student cannot check in  
- [ ] Attendance lines match batch roster  
- [ ] Staging UAT documented and passed  

## 6. Open questions

1. Portal (phone) or kiosk in classroom?  
2. One QR per day/session or stable per batch for whole period?  
3. Late / early policy?

## 7. Risks

Largest item in this meeting set. Needs separate design sign-off before build. Do not start without clarifying portal vs kiosk.
