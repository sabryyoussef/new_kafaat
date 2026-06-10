# Phase 4 — Program Enhancement Fields

**Model:** `op.program` in `edafaa_training_crm`

| Field | Type | Arabic label context | Tab |
|-------|------|---------------------|-----|
| `duration_text` | Char (translate) | مدة البرنامج | Main group |
| `training_language` | Selection ar/en/bilingual | لغة التدريب | Main group |
| `max_trainees` | Integer | الحد الأقصى للمتدربين | Main group |
| `available_schedules` | Text (translate) | المواعيد المتاحة | Delivery tab |
| `program_objectives` | Html (translate) | أهداف البرنامج | Description tab |
| `career_outcomes` | Html (translate) | النتائج المهنية | Description tab |

## Rules followed

- No new required constraints on legacy programs.
- Existing records load with empty optional fields.
- Content population is client data entry after fields exist.

## Files

- `models/op_program.py`
- `views/op_program_views.xml`
