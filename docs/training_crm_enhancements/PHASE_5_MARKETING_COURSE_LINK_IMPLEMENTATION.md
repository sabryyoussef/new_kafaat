# Phase 5 — Marketing & Course Linkage

**Model:** `op.program`

## Changes

### Course linkage

- `course_ids` — One2many(`op.course`, `program_id`) using existing OpenEduCat FK.
- `course_count` — computed integer.
- Smart button **Courses** on program form.
- **Linked Courses** notebook tab with list view.
- Tree view shows `course_count` (optional column).

### Marketing / media

- `brochure` — Binary attachment field with `brochure_filename`.
- `marketing_materials` — Text (translate).
- Existing `image_1920` from core retained on form header.

### Counts

- No separate accreditation/pricing models; counts not duplicated (motakamel-style counts deferred).

## Files

- `models/op_program.py`
- `views/op_program_views.xml`
- `tests/test_op_program.py` (`test_linked_courses`)
