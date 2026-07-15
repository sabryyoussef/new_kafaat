# Requirement Analysis — OP#354 / Odoo #45

**Subject:** Batch workflow — Arabic user guide  
**Priority:** Normal  
**Status:** **NOT IMPLEMENTED** (code exists; client Arabic guide missing)  
**Estimate:** 1–2 days (documentation)  
**Links:** [OP#354](https://master.tailcf9988.ts.net:10081/work_packages/354) · [Odoo #45](http://127.0.0.1:8069/web#id=45&model=project.task&view_type=form&db=sabry-test)

---

## 1. Client requirement

Provide a clear **Arabic explanation** of how **Batch** intake works and how to use it in the system.

## 2. Current system

| Component | Path | Role |
|-----------|------|------|
| Core | `batch_intake` | Upload → validate → process; **CSV only** (xlsx raises UserError) |
| Bridge | `edafaa_batch_intake` | Requires Schedule Batch; enriches `op.student`; menus |
| Wizard | `batch.trainee.assignment.wizard` | Multi-select trainees → course + batch |

**Flow:** Create intake → upload file → validate → set course/batch → process → create/link students → optional Assign to Batch.

### Docs today

- `batch_intake/README.md` — English, outdated  
- No Arabic client guide for Batch (unlike leave guide under `docs/op339_340/guides/`)

## 3. Gap

Users lack a client-facing Arabic walkthrough with screenshots. Excel limitation is undocumented for clients.

## 4. Proposed implementation

1. Write Arabic user guide (Markdown + HTML) covering create / process / assign  
2. Screenshots from `sabry-test` or TR_K19  
3. Explicit note: use CSV until Excel parsing is implemented  
4. Attach to OP#354 + Odoo #45; share with client  

**No code change required** unless client demands Excel support (separate WP).

## 5. Acceptance criteria

- [ ] Arabic guide covers intake + assign wizard  
- [ ] Staging screenshots included  
- [ ] Client can follow without developer help  

## 6. Open questions

1. Should Excel parsing be a follow-up development WP?  
2. Guide only for SIS `op.batch` intake, or also grants `Intake Batch`?

## 7. Risks

Low. Scope creep if Excel implementation is bundled with guide.
