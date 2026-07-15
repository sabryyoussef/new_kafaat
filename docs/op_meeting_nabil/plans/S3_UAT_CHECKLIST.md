# S3 UAT Checklist — OP#355

**Date:** 2026-07-15  
**DB:** sabry-test  
**Branch:** `feature/meeting-s3-355`  
**Module:** `edafaa_student_profile` `19.0.2.6.0`

## Field
- [x] Form shows `موظف المبيعات المسؤول` (`assigned_user_id`)
- [x] List optional column + search/group-by

## Wizard
- [x] Menu: Students → General → Excel assign to sales
- [x] Download template `.xlsx`
- [x] Import assigns `assigned_user_id`
- [x] Reject CSV for unknown student/staff
- [x] Overwrite works

## Automated
- [x] Unit `TestMeetingS3SalesAssign` 5/5
- [x] Playwright `meeting_s3` 3/3

## Delivery
- [x] OP [#365](https://master.tailcf9988.ts.net:10081/work_packages/365); #355 Closed
- [x] Odoo [#54](http://127.0.0.1:8069/web#id=54&model=project.task&view_type=form&db=sabry-test); #46 Done
