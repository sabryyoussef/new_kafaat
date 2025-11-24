# Sales Pools Phase 2 - Menu Implementation Status

## Overview
This document tracks the implementation status of all Sales Pools Phase 2 menus and features.

---

## ✅ COMPLETED MENUS (Working)

### 1. My Contacts
- **Location:** Intake Management > My Contacts
- **Action:** `grants_training_suite_v19.action_my_contacts`
- **File:** `views/salesperson_dashboard_views_simple.xml`
- **Status:** ✅ Working
- **Description:** Shows contacts assigned to the logged-in salesperson's pools
- **Features:**
  - Filtered by `pool_id.sales_person_id = uid`
  - List, Form, and Kanban views
  - Activity tracking fields visible

### 2. My Leads
- **Location:** Intake Management > My Leads
- **Action:** `grants_training_suite_v19.action_my_leads`
- **File:** `views/salesperson_dashboard_views_simple.xml`
- **Status:** ✅ Working
- **Description:** Shows leads linked to contacts in the salesperson's pools
- **Features:**
  - Filtered by `partner_id.pool_id.sales_person_id = uid`
  - List, Form, and Kanban views
  - Activity tracking and Pool information

---

## ⏸️ COMMENTED OUT / PENDING

### 3. Sales Dashboard
- **Location:** Intake Management > Sales Dashboard (COMMENTED OUT)
- **Action:** `action_salesperson_dashboard`
- **File:** `views/salesperson_dashboard_views_minimal.xml`
- **Status:** ⏸️ Commented out - Technical issue
- **Issue:** Action not being found during menu loading even though it's defined
- **Model:** `salesperson.dashboard` (TransientModel)
- **Possible Causes:**
  - TransientModel registration timing
  - Module loading order issue
  - Database transaction rollback
- **Files Involved:**
  - `models/salesperson_dashboard.py` - Model definition (EXISTS)
  - `views/salesperson_dashboard_views.xml` - Full views (NOT LOADED)
  - `views/salesperson_dashboard_views_minimal.xml` - Minimal action (LOADED)
  - `views/menu_views.xml` - Menu item (COMMENTED OUT line 49-55)
- **Next Steps:**
  - Investigate TransientModel loading in Odoo 18/19
  - Try creating as regular Model instead of TransientModel
  - Check if model needs to be registered differently

### 4. Pool Utilization Report
- **Location:** Reports > Pool Utilization Report (COMMENTED OUT)
- **Action:** `grants_training_suite_v19.action_pool_utilization_report_wizard`
- **File:** `views/pool_utilization_report_views.xml`
- **Status:** ⏸️ Commented out - Models not registered
- **Model:** `pool.utilization.report` (TransientModel)
- **Files Involved:**
  - `models/pool_utilization_report.py` - Model definition (EXISTS)
  - `views/pool_utilization_report_views.xml` - Views (LOADED but action commented)
  - `views/menu_views.xml` - Menu item (COMMENTED OUT line 192-196)
- **Features Planned:**
  - Number of leads distributed per Pool
  - Lead conversion performance per Sales Rep
  - Idle leads (no activity for X days)
  - Total Won leads per Pool
  - Tree, Graph, and Pivot views

### 5. Sales Rep Performance
- **Location:** Reports > Sales Rep Performance (COMMENTED OUT)
- **Action:** `grants_training_suite_v19.action_sales_rep_performance`
- **File:** `views/pool_utilization_report_views.xml`
- **Status:** ⏸️ Commented out - Models not registered
- **Model:** `pool.sales.rep.performance` (TransientModel)
- **Files Involved:**
  - `models/pool_utilization_report.py` - Model definition (EXISTS)
  - `views/pool_utilization_report_views.xml` - Views (LOADED but action commented)
  - `views/menu_views.xml` - Menu item (COMMENTED OUT line 197-201)
- **Features Planned:**
  - Sales Rep performance metrics
  - Conversion rates
  - Activity tracking
  - Reporting views

---

## 📋 IMPLEMENTATION DETAILS

### Models Status
| Model Name | Type | File | Imported | Registered |
|------------|------|------|----------|------------|
| `salesperson.dashboard` | TransientModel | `salesperson_dashboard.py` | ✅ Yes | ❓ Unknown |
| `pool.utilization.report` | TransientModel | `pool_utilization_report.py` | ✅ Yes | ❓ Unknown |
| `pool.sales.rep.performance` | TransientModel | `pool_utilization_report.py` | ✅ Yes | ❓ Unknown |

### View Files Status
| File | Loaded in Manifest | Status | Notes |
|------|-------------------|--------|-------|
| `salesperson_dashboard_views_simple.xml` | ❌ No | Not loaded | Has working actions for My Contacts/Leads |
| `salesperson_dashboard_views_minimal.xml` | ✅ Yes | Loaded | Minimal dashboard action only |
| `salesperson_dashboard_views.xml` | ❌ No | Commented out | Full dashboard with kanban/form |
| `activity_tracking_views.xml` | ✅ Yes | Loaded | Activity enhancements |
| `pool_utilization_report_views.xml` | ✅ Yes | Loaded | Report views |

### Security Status
| File | Loaded | Status | Notes |
|------|--------|--------|-------|
| `ir.rule.xml` | ✅ Yes | Working | Record rules for filtering by salesperson |
| `ir.model.access.phase2.xml` | ❌ No | Commented out | Access rules for new models |

---

## 🐛 KNOWN ISSUES

### Issue 1: TransientModel Actions Not Found
**Symptom:** `ValueError: External ID not found in the system: grants_training_suite_v19.action_salesperson_dashboard`

**Affected:**
- Sales Dashboard
- Pool Utilization Report
- Sales Rep Performance

**Root Cause:** Unknown - possibly related to:
1. TransientModel registration timing in Odoo's ORM
2. XML loading order vs Python model registration
3. Transaction rollback during upgrade

**Workaround:** Menus commented out for now

**Possible Solutions to Try:**
1. Convert TransientModels to regular Models
2. Load view files in different order
3. Use `noupdate="1"` in data tags
4. Create actions programmatically in Python
5. Check Odoo version compatibility (18 vs 19)

---

## 📝 TODO LIST

### High Priority
- [ ] Fix TransientModel action loading issue
- [ ] Uncomment and test Sales Dashboard menu
- [ ] Uncomment and test Pool Utilization Report menu
- [ ] Uncomment and test Sales Rep Performance menu
- [ ] Re-enable `ir.model.access.phase2.xml` security file

### Medium Priority
- [ ] Test all dashboard KPIs with real data
- [ ] Verify record rules are working correctly
- [ ] Add more activity tracking features
- [ ] Enhance reporting views with filters

### Low Priority
- [ ] Delete unused `salesperson_dashboard_views_simple.xml`
- [ ] Clean up debug logging in models
- [ ] Optimize computed field performance
- [ ] Add demo data for Phase 2 features

---

## 📚 REFERENCES

### Related Files
- `__manifest__.py` - Module configuration and data loading order
- `models/__init__.py` - Model imports
- `security/ir.rule.xml` - Record rules for data filtering
- `SALES_DASHBOARD_DEBUG.md` - Detailed debugging notes

### Odoo Documentation
- TransientModel: https://www.odoo.com/documentation/18.0/developer/reference/backend/orm.html#transient-models
- Actions: https://www.odoo.com/documentation/18.0/developer/reference/backend/actions.html
- Menus: https://www.odoo.com/documentation/18.0/developer/reference/backend/views.html#menus

---

**Last Updated:** 2025-11-24 00:37 GMT
**Module Version:** 19.0.1.0.0
**Odoo Version:** 19.0

