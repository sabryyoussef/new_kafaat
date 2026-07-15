# S2 UAT Checklist — OP#352 / #354

**Date:** 2026-07-15  
**DB:** sabry-test  
**Branch:** `feature/meeting-s2-352-354`  
**Module:** `edafaa_student_profile` `19.0.2.5.0` (+ portal sync `19.0.1.1.0`)

## #352 application_status

### Automated

- [x] Unit tests `TestMeetingS2StudentProfile` — 5/5
- [x] Default create → `under_review`
- [x] Manual write to accepted / rejected / cancelled
- [x] Form/list/search arch contain `application_status` + `حالة الطالب`
- [x] Registration state map helper covered

### Manual / Playwright

- [x] Form shows `حالة الطالب` badge (`s2_352_student_form_application_status.png`)
- [x] List/search include field (`s2_352_students_list_application_status.png`)
- [x] ملغي does **not** archive (`active` stays True)

## #354 Batch Arabic guide

- [x] `USER_GUIDE_BATCH_AR.md` + `.html` present
- [x] Screenshots under `guides/screenshots/batch_*.png`
- [x] CSV-only / Excel unsupported note present
- [x] Attached to delivery packages

## Delivery

- [x] OP delivery [#363](https://master.tailcf9988.ts.net:10081/work_packages/363) under #87
- [x] Odoo delivery [#51](http://127.0.0.1:8069/web#id=51&model=project.task&view_type=form&db=sabry-test) under #41
- [x] OP #352/#354 Closed; Odoo #43/#45 Done
- [x] Playwright `tests/playwright/meeting_s2/` — 3/3
