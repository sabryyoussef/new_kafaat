# Student Profile — Screenshot Guide

**Purpose:** Capture evidence for client UAT / delivery review.  
**Branch:** `feature/student-profile-p1-crs-code`  
**Suggested format:** PNG, full form visible, English UI (Arabic fields where relevant)

---

## Capture checklist

| # | Screenshot | Where to capture | What to show | Done |
|---|------------|------------------|--------------|------|
| 1 | **Course CRS code** | OpenEduCat → Configuration → Course Management → Courses → form | Auto code `CRS-XXXX` in **Code** field (or placeholder hint) | ☐ |
| 2 | **Program PRG code** | Configuration → Programs → form | Auto code `PRG-XXXX` in **Code** field | ☐ |
| 3 | **Student required fields** | Students → Student form (top/sheet) | Arabic Name, English Name, ID, email, phone, birth date, address (street, city, country) | ☐ |
| 4 | **Family tab** | Student form → **Family** | Parents (`parent_ids`) + **Siblings** list with two linked students | ☐ |
| 5 | **Training Summary** | Student form sheet → **Training Summary** group | Status badge, current course/batch, running/completed counts | ☐ |
| 6 | **Courses tab** | Student form → **Courses** | List with course, batch, roll number, running/finished status | ☐ |
| 7 | **Course Skills tab** | Course form → **Skills** (after Subjects) | `skill_ids` tags; **Subjects** tab still present in notebook | ☐ |
| 8 | **Program Skills tab** | Program form → **Skills** notebook page | Program skills tags | ☐ |
| 9 | **Certificate form** | Students → Configuration → **Course Certificates** (or smart button) | Certificate number, student, course, batch, state, PDF attachment | ☐ |
| 10 | **Courses tab + certificate** | Student **Courses** tab — finished row | Certificate number column; Issue/Download/Send actions as applicable | ☐ |
| 11 | **Email / mail record** | After **Send Email** on certificate | Either: success notification **or** Settings → Technical → Email → `mail.mail` row with attachment | ☐ |

---

## Optional supporting shots

| Shot | Purpose |
|------|---------|
| Skill master list | Configuration → Course Management → **Skills** |
| Student **Certificates** smart button | Stat button on student form when count > 0 |
| Validation error (missing email) | Send Email blocked with clear message |
| Portal staff registration (3B) | ID/address fields before approval |

---

## Tips

1. Use **one test student** with a finished enrollment and issued certificate for shots 6, 9, 10, 11.
2. Use **two students + shared parent** for shot 4.
3. Blur/redact real PII if sharing outside client environment.
4. File naming convention: `uat-<area>-<short-desc>.png`  
   Example: `uat-courses-tab-certificate-finished.png`

---

## Delivery package

Suggested folder for client:

```
uat-screenshots/
  01-course-crs-code.png
  02-program-prg-code.png
  03-student-required-fields.png
  04-family-siblings.png
  05-training-summary.png
  06-courses-tab.png
  07-course-skills.png
  08-program-skills.png
  09-certificate-form.png
  10-courses-certificate-row.png
  11-email-mail-record.png
```

Attach with `UAT_CHECKLIST.md` completed sign-off.

---

## Known gaps (do not screenshot as delivered)

- Portal certificate download page (out of scope)
- Polished certificate PDF design (minimal template only)
- Live SMTP inbox delivery (unless SMTP configured)
