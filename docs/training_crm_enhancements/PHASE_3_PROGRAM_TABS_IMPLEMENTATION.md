# Phase 3 — Program Tabs & Arabic Labels

**Module:** `edafaa_training_crm`

## Tab structure (notebook pages on `op.program` form)

| Tab (Arabic) | Technical name | Content fields |
|--------------|----------------|----------------|
| وصف البرنامج | `description_tab` | `description_html`, `program_objectives`, `career_outcomes` |
| الاعتمادات والشهادات | `accreditations_tab` | `accreditations_html` |
| الفئة المستهدفة | `target_audience_tab` | `target_audience_html` |
| طريقة التقديم | `delivery_tab` | `delivery_html`, `available_schedules` |
| التسعير والرسوم | `pricing_tab` | `pricing_html` |
| متطلبات الالتحاق | `credentials_tab` | `credentials_html` |
| التسويق والإعلان | `marketing_tab` | `brochure`, `marketing_materials` |
| الإدارة الداخلية | `administration_tab` | `approved_by_id`, `approved_date`, `admin_notes` |
| Linked Courses | `linked_courses_tab` | `course_ids` list |
| Skills (existing) | `skills` | From `edafaa_student_profile` — preserved |

## Approach

- Lightweight Html/Text fields per section (not separate motakamel sub-models).
- Arabic titles set via `string` on `<page>` elements as client requested.
- Inherit priority 30 on base program form; pages appended to notebook from `edafaa_student_profile`.

## Files

- `views/op_program_views.xml`
