# Development Plan — OP#358 / Odoo #49

**Title:** Batch attendance + QR Code per batch  
**Sprint:** S5  
**Effort:** 3–5 weeks  
**Module:** `edafaa_batch_attendance`  
**Branch:** `feature/meeting-s5-358`

---

## Design lock (fixed 2026-07-15)

| Topic | Choice |
|-------|--------|
| Check-in UX | **1A — Student portal (phone)** — logged-in portal user |
| QR lifetime | **Stable per batch** — regenerate revokes old URL |
| Late policy | Allow after start; `late=True` if &gt; **15 minutes** after sheet QR open |

---

## Phases

| Phase | Weeks | Deliverable |
|-------|-------|-------------|
| 0 Docs + branch | 0.5 d | This lock + OP/Odoo comment |
| 1 Batch QR | 1 | Token + QR image on `op.batch` |
| 2 Sheet bridge | 1 | Auto register/sheet + line upsert |
| 3 Portal check-in | 1–1.5 | `/attendance/batch/<token>` |
| 4 Security & audit | 0.5 | Active flag, rate limit, check-in log |
| 5 UAT | 1 | Playwright + TR_K19 |

---

## Module

`custom_addons/edafaa_batch_attendance` — depends on `openeducat_attendance`, `openeducat_core`, `portal`, `website`, `student_enrollment_portal`.

### `op.batch`

- `attendance_qr_token`, `attendance_qr_url`, `attendance_qr_image`, `attendance_qr_active`
- `action_generate_qr` / `action_regenerate_qr` / toggle active

### Check-in

1. Resolve batch by token + active  
2. Resolve `op.student` from `request.env.user` (user_id / partner / email; link `user_id` if missing)  
3. Require `op.student.course` with `batch_id` + `state='running'`  
4. Ensure today’s `op.attendance.register` + sheet (`start`)  
5. Upsert `op.attendance.line` (`present`; `late` after grace)  
6. Log result; rate-limit failed/spam attempts  

### Portal route

```text
GET /attendance/batch/<token>   auth=user, website=True
```

---

## UAT scenarios

1. Enrolled portal student → present  
2. Re-scan same day → already checked in  
3. Non-enrolled → rejected  
4. Regenerated / inactive QR → rejected  
5. After grace → present + late  
6. Sheet roster consistent  

## Out of scope

Kiosk, daily QR, GPS, enterprise barcode/kiosk, S4 translation redo.
