# S5 UAT Checklist — OP#358

**Date:** 2026-07-15  
**DB:** sabry-test  
**Branch:** `feature/meeting-s5-358`  
**Module:** `edafaa_batch_attendance` `19.0.1.0.0`

## Design lock
- [x] 1A portal (phone)
- [x] Stable QR per batch
- [x] Late grace 15 minutes

## Batch QR
- [x] Generate QR on batch form
- [x] QR image + URL visible
- [x] Regenerate invalidates old token
- [x] Deactivate rejects check-in

## Portal check-in
- [x] Enrolled portal student → present
- [x] Re-scan same day → already checked in
- [x] Non-enrolled → rejected
- [x] After grace → present + late

## Attendance sheet
- [x] Today’s register/sheet auto-created
- [x] Lines match check-ins

## Automated
- [x] Unit tests 6/6
- [x] Playwright `meeting_s5` 3/3

## Delivery
- [x] OP #358 updated
- [x] Odoo #49 updated
- [x] TR_K19 upgraded
