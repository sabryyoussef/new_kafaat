# OP#206 Delivery Work Package

**Subject:** Delivery — UAT retest fixes for OP#86 (#206)  
**Branch:** `feature/op206-uat-retest-op86`  
**Parent:** OpenProject #87 / related #86 / #206  

## Package layout

```
docs/op206/delivery/
├── README.md                 ← this file
├── DELIVERY_MESSAGE_AR.txt   ← short message for implementor / Chatwoot
├── notes/
│   ├── FIX_NOTES.md
│   ├── FIX_NOTES_AR.md
│   ├── OP206_UAT_FIX_REPORT.md
│   ├── PLAYWRIGHT_PROOF_EXPLAIN.md
│   ├── UAT_CHECKLIST.md
│   └── unit_test_run_2026-07-04.log
└── screenshots/
    ├── r1_students_list.png
    ├── r1_group_by_menu.png
    ├── r1_group_by_current_course.png
    ├── r2_trainee_form_labels.png
    ├── r2_registration_form_labels.png
    ├── r3_no_blood_group.png
    └── r4_registration_source_fields.png
```

## Screenshot index

| File | Proves |
|------|--------|
| `r1_students_list.png` | Students list after upgrade |
| `r1_group_by_menu.png` / `r1_group_by_current_course.png` | Group By Current Course (المقرر الحالي) |
| `r2_trainee_form_labels.png` | Arabic labels + mapped ID/phone/address/specialization |
| `r2_registration_form_labels.png` | Registration form Arabic profile fields |
| `r3_no_blood_group.png` | Blood Group not visible |
| `r4_registration_source_fields.png` | رقم التسجيل + نوع المصدر on student profile |

## Zip attachment

See `OP206_DELIVERY_PACKAGE.zip` in this folder (or repo root `docs/op206/`).
