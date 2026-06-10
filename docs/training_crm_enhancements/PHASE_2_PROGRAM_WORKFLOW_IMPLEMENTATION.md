# Phase 2 — Program Workflow Implementation

**Module:** `edafaa_training_crm`  
**Model:** `op.program`

## Changes

- Added `state` Selection with five lifecycle values (bilingual labels):
  - `draft` — Draft / مسودة
  - `review` — Under Review / قيد المراجعة
  - `approved` — Approved / معتمد
  - `published` — Published / منشور — متاح للتسجيل
  - `archived` — Archived / أرشيف — غير نشط
- Default `draft`; `required=True`; `tracking=True`; `copy=False`.
- Header statusbar on program form.
- Transition buttons: Submit for Review, Approve, Publish, Archive, Reset to Draft.
- `action_archive_program` sets `active=False`; reset restores `active=True`.
- `approved_by_id` and `approved_date` set on approve.

## Scope note

Published state is **workflow/UI only** in this phase. It does not automatically change website enrollment or batch availability unless a future integration reads `state`.

## Files

- `models/op_program.py` (state + actions)
- `views/op_program_views.xml` (header/statusbar/buttons)
