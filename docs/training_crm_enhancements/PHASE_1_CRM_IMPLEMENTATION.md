# Phase 1 — CRM Implementation

**Module:** `edafaa_training_crm`  
**Date:** 2026-06-07

## Changes

### Sales Team lead target (`crm.team`)

- Added `lead_target` (integer, monthly lead count goal).
- Added computed `lead_count_month` and `lead_target_progress`.
- Added `update_lead_target()` API mirroring sale's invoiced target pattern.
- Inherited `sale.crm_team_salesteams_view_form` to show lead target instead of invoicing target; hid `invoiced_target`.
- Inherited kanban dashboard to expose lead target fields.

### Students wording (CRM scope)

- CRM menu `Customers` renamed to **Students** and action redirected to `openeducat_core.act_open_op_student_view_2` (`op.student` list/form).
- Accounting and Sales Order "Customer" labels unchanged.

### Student contact bridge (`res.partner`)

- Added `birth_date` and `id_number` on partner for student profile mapping.
- Added computed `op_student_id` and smart button **Student** on contact form.
- On create/write when `is_student=True`, auto-creates `op.student` when minimum profile data is present (name, email, phone, street, city, country, birth date, ID).
- Uses `edafaa_skip_student_sync` context to prevent recursion during `op.student` delegation writes.

## Assumptions

- Auto-create requires all minimum fields; incomplete contacts remain in Contacts only until completed.
- `name_arabic` defaults to contact `name` when auto-creating (client can edit in Students form).
- Lead target replaces invoicing target on team form in sale-inherited view; revenue target still stored but hidden.

## Files

- `models/crm_team.py`
- `models/res_partner.py`
- `views/crm_team_views.xml`
- `views/crm_menu_views.xml`
- `views/res_partner_views.xml`
- `tests/test_crm_team.py`
- `tests/test_res_partner.py`
