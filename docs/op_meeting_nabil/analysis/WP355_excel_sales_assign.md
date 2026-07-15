# Requirement Analysis — OP#355 / Odoo #46

**Subject:** Excel bulk assign trainees to sales staff  
**Priority:** Normal  
**Status:** **NOT IMPLEMENTED**  
**Estimate:** 5–7 days  
**Links:** [OP#355](https://master.tailcf9988.ts.net:10081/work_packages/355) · [Odoo #46](http://127.0.0.1:8069/web#id=46&model=project.task&view_type=form&db=sabry-test)

---

## 1. Client requirement

Distribute trainee names to **sales staff** by uploading an **Excel** file — not only one-by-one assignment.

## 2. Current system

| Feature | Exists? | Notes |
|---------|---------|-------|
| Trainee → sales user field on `op.student` | **No** | Portal `user_id` is portal login, not salesperson |
| Excel import for trainee→staff map | **No** | |
| Batch intake CSV | Yes | Creates students, not sales assignment |
| Assign to Batch wizard | Yes | Assigns to course/batch only |
| `contact_pool_distribution` (grants) | Partial | Assigns **partners** to agents; no Excel; not `op.student` |
| `assigned_agent_id` on `gr.student` | Yes | Grants stack only |

## 3. Gap

No SIS feature to bulk-map trainees to sales employees via Excel.

## 4. Proposed implementation

1. Add `assigned_user_id` (Many2one `res.users`) or `assigned_employee_id` on `op.student`  
2. Excel template columns (TBD with client), e.g. `id_number` + `staff_email`  
3. Import wizard: parse → validate → write assignments → download rejected rows CSV  
4. Security: who can run import; record rules if needed  
5. UAT with sample file  

**Module:** new wizard in `edafaa_student_profile` or `edafaa_training_crm`

## 5. Acceptance criteria

- [ ] Excel template available  
- [ ] Upload assigns trainees to correct sales staff  
- [ ] Rejected rows exported with reason  
- [ ] UAT on staging  

## 6. Open questions

1. Columns: national ID + staff email vs name + employee code?  
2. Target model: `res.users`, `hr.employee`, or CRM salesperson on `crm.lead`?  
3. Overwrite existing assignment or fail?

## 7. Risks

High ambiguity until column format and target model are confirmed. Grants `assigned_agent_id` is a reference pattern, not a drop-in.
