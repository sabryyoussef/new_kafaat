# Step 1 — Auto Course Code `CRS-XXXX` — Analysis

**Step:** 1  
**Requirement:** A — Automatic Course Code `CRS-XXXX`  
**Date:** 2026-06-07  
**Status:** Analysis complete — **no implementation**  
**Analyst scope:** Code inspection + `sabry-test` database queries only

---

## 1. Executive Summary

| Question | Conclusion |
|----------|------------|
| Target model? | **`op.course`** (`openeducat_core`) — confirmed |
| Reuse existing `code` field? | **Yes** — no new field required |
| Existing course sequence? | **No** — none in codebase or `sabry-test` |
| Existing `create()` on `op.course`? | **No** — safe to add via `edafaa_student_profile` inherit |
| Manual code policy | **Empty → auto `CRS-XXXX`; non-empty → preserve** |
| Legacy migration needed? | **`sabry-test`: no** (0 courses). Other DBs: forward-only; no retroactive assignment without separate approval |

---

## 2. Target Model — `op.course`

**File:** `localaddons/openeducat_core/models/course.py`

| Property | Value |
|----------|-------|
| `_name` | `op.course` |
| `_inherit` | `mail.thread` |
| Primary identifier for client | Yes — used by enrollments, portal, timetable, fees, motakamel links |

### Field: `code`

```python
code = fields.Char('Code', size=16, required=True)
```

| Aspect | Detail |
|--------|--------|
| Type | `Char`, max 16 characters |
| ORM `required` | `True` — record cannot be saved without a value |
| UI today | Editable on form (`openeducat_core/views/course_view.xml` line 42) |
| List/search | Shown in tree and searchable |
| Uniqueness | SQL constraint `_unique_course_code`: `unique(code)` |

**Implication:** Auto-generation must run in `create()` **before** insert, assigning `code` when the caller leaves it empty/whitespace. The ORM `required=True` is satisfied by the generated value.

### Other relevant fields (unchanged by Step 1)

- `name` — required, translatable
- `program_id` — Many2one `op.program`
- `subject_ids` — Many2many `op.subject`
- No `default` on `code`
- No `@api.model_create_multi` / `create()` override in core

---

## 3. Uniqueness Constraint

```python
_unique_course_code = models.Constraint('unique(code)',
                                        'Code should be unique per course!')
```

| Scenario | Behavior |
|----------|----------|
| Auto-generated sequential codes | Unique by sequence design |
| Manual code on create | Must not duplicate existing `code` — DB raises constraint error |
| Manual code on write | Same uniqueness applies |
| Empty string `''` | Would violate `required` unless `create()` fills it first |

**Proposed sequence format:** prefix `CRS-`, padding `4` → `CRS-0001` … `CRS-9999` (8 chars, within `size=16`).

---

## 4. Existing Sequence Search

### Codebase (`/opt/localaddons`)

| Sequence code | Model | Prefix | Related to `op.course`? |
|---------------|-------|--------|------------------------|
| `motakamel.program` | `motakamel.program` | `PROG-` | No |
| `student.registration` | `student.registration` | varies | No |
| `course.enrollment.request` | `course.enrollment.request` | varies | No (enrollment request name, not course code) |
| `op.admission`, `op.attendance.sheet`, etc. | other models | varies | No |

**Result:** No `ir.sequence` for `op.course.code` in any local addon.

### Database `sabry-test` (2026-06-07)

```sql
SELECT id, name, code, prefix, padding
FROM ir_sequence
WHERE code ILIKE '%course%' OR name ILIKE '%course%' OR prefix ILIKE '%CRS%';
-- (0 rows)
```

---

## 5. Existing Records — Code Presence

### `sabry-test`

| Metric | Value |
|--------|-------|
| `op_course` row count | **0** |
| Rows with null/blank `code` | **0** |

No legacy courses on the primary test database. Step 1 can use sequence `number_next = 1` without conflict on `sabry-test`.

### Demo / seed data (not loaded on `sabry-test`)

**File:** `localaddons/openeducat_core/demo/op.course.csv`

- 60 demo courses with **semantic manual codes** (e.g. `BCA-CC-SEM-1`, `MCA-BD-SEM-1`, `CT-CS`)
- Pattern is **not** `CRS-XXXX`
- Loaded only when OpenEduCat demo data is installed

**Script:** `localaddons/demo_data_scripts/insert_demo_courses.py`

- Creates courses with explicit codes: `CBPLC-2026`, `PHRI-2026`, `PMP-2026`

### Migration stance (proposed — needs Approval 1)

| Policy | Recommendation |
|--------|----------------|
| Existing records | **Leave unchanged** — no bulk backfill |
| New creates (UI/API/import) | Auto-fill when `code` empty; preserve when provided |
| Retroactive `CRS-` assignment | **Out of scope** for Step 1 — separate migration step if ever needed |
| Sequence start number | `1` on fresh DB; on DBs with existing courses, set `number_next` after max existing `CRS-*` if any (none today) |

---

## 6. Existing Inherits on `op.course`

| Module | File | What it adds | `create()` override? |
|--------|------|--------------|----------------------|
| `openeducat_fees` | `models/course.py` | `fees_term_id` | No |
| `student_enrollment_portal` | `models/course.py` | `image_1920` (duplicate declare) | No |

**No conflicting `create()` logic** on `op.course` today. `edafaa_student_profile` inherit chains cleanly after `super().create()`.

### Downstream consumers of `course.code` (read-only impact)

- `student_enrollment_portal` — portal templates display `course.code`
- `motakamel` — website templates display `course.code`
- Fees, timetable, exam, library — FK/reference by `op.course` id; code display incidental

**Portal impact for Step 1:** None beyond displaying the stored code after create (auto or manual).

---

## 7. Views to Inherit

### Core views (`openeducat_core`)

| XML ID | Type | Priority | Inherit for Step 1? |
|--------|------|----------|---------------------|
| `openeducat_core.view_op_course_form` | form | 8 | **Yes — primary** |
| `openeducat_core.view_op_course_tree` | list | 8 | Optional (no change required — `code` already listed) |
| `openeducat_core.view_op_course_search` | search | 8 | No change required — `code` already searchable |
| `openeducat_core.view_op_course_pivot` | pivot | 8 | No |

### Existing third-party inherits (do not modify)

| XML ID | Module | Priority | Change |
|--------|--------|----------|--------|
| `view_op_course_form_pt_inherit` | `openeducat_fees` | 9 | None — adds `fees_term_id` after `evaluation_type` |
| `view_op_course_form_image_inherit` | `student_enrollment_portal` | 10 | None — adds image inside header |

**Proposed view change (Step 1):** Inherit `view_op_course_form`:

- Add `placeholder` on `code`: e.g. "Auto: CRS-0001 if empty"
- Optionally `readonly="not id"` after first save ( **defer** — keep editable unless client requests lock; manual override policy applies at create time)

Tree/search: **no inherit required** for MVP.

---

## 8. Manual Code Policy (proposed)

| Input on create | Result |
|-----------------|--------|
| `code` omitted, `False`, `None`, or whitespace only | Assign `ir.sequence.next_by_code('edafaa.op.course')` → `CRS-0001`, … |
| `code` provided with non-whitespace value | **Preserve exactly** — do not consume sequence |
| RPC/API `create({'name': 'X'})` without `code` | Auto-generate |
| Import with `code` column filled | Preserve per row |
| Import with blank `code` | Auto-generate per row |
| Duplicate manual `code` | DB uniqueness error (unchanged) |

### `create()` pseudocode (for implementation note — not coded yet)

```python
@api.model_create_multi
def create(self, vals_list):
    Seq = self.env['ir.sequence']
    for vals in vals_list:
        code = vals.get('code')
        if not code or not str(code).strip():
            vals['code'] = Seq.next_by_code('edafaa.op.course') or _('New')
    return super().create(vals_list)
```

**Edge case:** If sequence misconfigured and returns falsy, fallback `'New'` would fail uniqueness on second record — implementation must ensure sequence XML is loaded and tested.

---

## 9. Technical Plan (for Approval 1)

### Addon: `edafaa_student_profile` (created at Approval 2)

| Item | Plan |
|------|------|
| **Depends** | `openeducat_core` only |
| **Model inherit** | `op.course` — `create()` override only |
| **New fields** | None |
| **Reused fields** | `code` |
| **Data** | `data/course_sequence.xml` — `ir.sequence` `code=edafaa.op.course`, `prefix=CRS-`, `padding=4`, `company_id=False` |
| **Views** | `views/course_views.xml` — inherit form, placeholder/help on `code` |
| **Security** | No new models → no `ir.model.access.csv` change |
| **Sequence impact** | **Yes** — one new sequence |
| **Portal impact** | **None** |
| **Report/email impact** | **None** |
| **Rollback** | Uninstall `edafaa_student_profile` → removes sequence + inherit; existing course codes remain |

### Files expected (Approval 2)

```
edafaa_student_profile/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── course.py
├── data/
│   └── course_sequence.xml
└── views/
    └── course_views.xml
```

Docs (this step):

- `/opt/docs/student_profile/step-01-auto-course-code-analysis.md` (this file)
- `step-01-auto-course-code-implementation.md` — after Approval 2
- `step-01-auto-course-code-test-result.md` — after testing

---

## 10. Test Plan

| ID | Test case | Steps | Expected |
|----|-----------|-------|----------|
| T1.1 | Auto-generate on empty code | Install module on `sabry-test`; create course with name only | `code` = `CRS-0001` |
| T1.2 | Sequential increment | Create second course without code | `code` = `CRS-0002` |
| T1.3 | Manual code preserved | Create with `code=CUSTOM-01` | `code` = `CUSTOM-01`; next auto still `CRS-0003` (sequence not consumed for manual) |
| T1.4 | Whitespace-only code | Create with `code='   '` | Treated as empty → auto `CRS-XXXX` |
| T1.5 | Duplicate manual code | Create two with same manual code | IntegrityError / validation on second |
| T1.6 | Form display | Open auto-created course | `code` visible in form and list |
| T1.7 | Search | Search by `CRS-0001` | Course found |
| T1.8 | Module upgrade | Upgrade module | Sequence not duplicated; existing codes unchanged |

**Validation method:** Odoo shell or UI on `sabry-test` + SQL verify `op_course.code` and `ir_sequence.number_next`.

---

## 11. Risks and Rollback

| Risk | Level | Mitigation |
|------|-------|------------|
| `size=16` too small for future padding | Low | Padding 4 sufficient for 9999 courses; increase padding only with approval |
| Conflict with semantic legacy codes | Low | Auto only when empty; legacy codes untouched |
| Sequence not loaded on install | Medium | Test T1.1; manifest must list `data/course_sequence.xml` |
| Multiple `create()` inherits later | Low | Always call `super().create()`; document MRO |
| Fees module requires `fees_term_id` on form | Medium | Unrelated to code — course create may still need `fees_term_id` if fees installed (pre-existing) |

**Rollback plan:** Uninstall `edafaa_student_profile`; manually delete `ir.sequence` record `edafaa.op.course` if orphaned; course records retain assigned codes.

---

## 12. Pre-Implementation Checklist

- [x] Impacted model: `op.course`
- [x] Impacted view: `openeducat_core.view_op_course_form` (inherit)
- [x] Reused fields: `code`
- [x] New fields: none
- [x] Sequence impact: yes — `edafaa.op.course`, prefix `CRS-`, padding 4
- [x] Security impact: none
- [x] Portal impact: none
- [x] Report/email impact: none
- [x] Test scenarios: T1.1–T1.8
- [x] Rollback plan: documented §11

---

## 13. Evidence References

| Source | Location |
|--------|----------|
| Course model | `localaddons/openeducat_core/models/course.py` |
| Course views | `localaddons/openeducat_core/views/course_view.xml` |
| Fees inherit | `localaddons/openeducat_fees/models/course.py`, `views/course_view.xml` |
| Portal inherit | `localaddons/student_enrollment_portal/models/course.py`, `views/course_view.xml` |
| Demo codes | `localaddons/openeducat_core/demo/op.course.csv` |
| DB: `sabry-test` | `op_course` count = 0; no course sequences |

---

## 14. Approvals

| Gate | Status | Reply token |
|------|--------|-------------|
| Approval 1 — this analysis | **Pending** | `Approved — Step 1 analysis` |
| Approval 2 — implementation | **Pending** | `Approved — Step 1 implementation` |

See **§15** below and master plan §5 for the **APPROVAL REQUIRED — IMPLEMENTATION** block.

---

## 15. APPROVAL REQUIRED — IMPLEMENTATION

*(Posted for Approval 2 — do not code until explicit approval)*

```
APPROVAL REQUIRED — IMPLEMENTATION

Step: 1
Requirement: A — Auto Course Code CRS-XXXX
Analysis document: /opt/docs/student_profile/step-01-auto-course-code-analysis.md
Current finding: op.course.code is manual required Char with unique constraint; no sequence;
  no create() override; sabry-test has 0 courses; no CRS sequence in DB.
Approved target model: op.course (inherit in edafaa_student_profile)
Approved fields: Reuse code only — no new fields
Approved views: Inherit openeducat_core.view_op_course_form (placeholder on code);
  no tree/search inherit required for MVP
Files expected to change:
  - edafaa_student_profile/__init__.py
  - edafaa_student_profile/__manifest__.py
  - edafaa_student_profile/models/__init__.py
  - edafaa_student_profile/models/course.py
  - edafaa_student_profile/data/course_sequence.xml
  - edafaa_student_profile/views/course_views.xml
Security impact: None — no new models or ACL
Sequence impact: Yes — ir.sequence code edafaa.op.course, prefix CRS-, padding 4, number_next 1
Portal impact: None — portal reads stored course.code
Report/email impact: None
Risk: Low — isolated inherit; legacy codes untouched; fees_term_id pre-existing constraint if fees installed
Rollback plan: Uninstall edafaa_student_profile; delete orphan sequence; codes on records preserved
Test cases to run: T1.1, T1.2, T1.3, T1.4, T1.5, T1.6, T1.7, T1.8
```

---

*End of Step 1 analysis. No Odoo code written.*
