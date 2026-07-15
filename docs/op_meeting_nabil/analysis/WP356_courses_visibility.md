# Requirement Analysis — OP#356 / Odoo #47

**Subject:** Investigate — limited courses visible in system  
**Priority:** High  
**Status:** **PARTIAL** (likely UX/ACL/data; not a hard two-record ir.rule bug)  
**Estimate:** 0.5–1 day investigation  
**Links:** [OP#356](https://master.tailcf9988.ts.net:10081/work_packages/356) · [Odoo #47](http://127.0.0.1:8069/web#id=47&model=project.task&view_type=form&db=sabry-test)

---

## 1. Client requirement

Fix/explain why **not all courses** appear (client reports only a subset).

## 2. Current system

| Mechanism | Evidence | Effect |
|-----------|----------|--------|
| Courses menu ACL | `edafaa_kafaat_sis/views/menu_views.xml` | Standalone Courses menu → **SIS admin only** |
| Program → Linked Courses | `edafaa_training_crm/models/op_program.py` | Domain `program_id = this program` |
| `ir.rule` on `op.course` | None found | No hard record limit of “two courses” |
| Base action domain | `openeducat_core` courses action | Empty domain `[]` for admins |

**Most likely:** Non-admin users only see Program → Linked Courses for the open program (often 1–2 courses).

## 3. Gap

Root cause not yet proven on TR_K19 with the client’s exact screen + user. No findings attached yet.

## 4. Proposed investigation plan

1. Get screenshot + menu breadcrumb from client  
2. Run on TR_K19:

```sql
SELECT id, name, code, program_id, active FROM op_course ORDER BY id;
SELECT active, COUNT(*) FROM op_course GROUP BY active;
SELECT p.id, p.name, COUNT(c.id)
FROM op_program p
LEFT JOIN op_course c ON c.program_id = p.id AND c.active
GROUP BY p.id, p.name;
```

3. Check reporter’s groups (`group_sis_admin` vs user)  
4. Document outcome: data / domain / ACL / genuine bug  
5. Remediate (data, training, or code)  

## 5. Acceptance criteria

- [ ] Root cause documented  
- [ ] Fix or data remediation if needed  
- [ ] Client screen re-verified  
- [ ] Findings attached to OP#356 / Odoo #47  

## 6. Open questions

1. Exact menu path / screen?  
2. Which user login sees the issue?  

## 7. Risks

Low if by-design Program scoping — risk is reopening as a “bug” that needs training, not code.
