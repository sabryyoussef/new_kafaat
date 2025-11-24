# Sales Dashboard Menu Investigation & Fix

## Problem
The "Sales Dashboard" menu item was causing an error:
```
ValueError: External ID not found in the system: grants_training_suite_v19.action_salesperson_dashboard
```

## Root Cause Analysis

### 1. Model Definition ✓
- **File:** `models/salesperson_dashboard.py`
- **Status:** EXISTS and properly defined
- **Model Name:** `salesperson.dashboard`
- **Type:** `TransientModel` (correct for dashboard)
- **Imported:** YES in `models/__init__.py` (line 71)

### 2. View File Issue ✗
- **Manifest was loading:** `views/salesperson_dashboard_views_simple.xml`
- **This file contained:**
  - `action_my_contacts` ✓
  - `action_my_leads` ✓
  - `action_salesperson_dashboard` ✗ MISSING!

- **Full file exists:** `views/salesperson_dashboard_views.xml`
- **This file contains:**
  - `view_salesperson_dashboard_kanban` (line 5-89)
  - `view_salesperson_dashboard_form` (line 92-118)
  - `action_salesperson_dashboard` (line 121-135) ✓
  - `action_my_contacts` (line 138-152)
  - `action_my_leads` (line 155-169)
  - Additional list/search views for contacts and leads

### 3. Security Access ✓
- **File:** `security/ir.model.access.phase2.xml`
- **Status:** Properly defined for both managers and salesmen
- **Loaded:** After views (correct order)

## The Fix

### Change 1: Update Manifest
**File:** `__manifest__.py` line 75

**Before:**
```python
'views/salesperson_dashboard_views_simple.xml',
```

**After:**
```python
'views/salesperson_dashboard_views.xml',  # Full dashboard with kanban/form views
```

### Change 2: Enable Menu Item
**File:** `views/menu_views.xml`

**Before:**
```xml
<!-- Temporarily commented out - model not registered yet
<menuitem
    id="menu_grants_training_sales_dashboard"
    name="Sales Dashboard"
    action="grants_training_suite_v19.action_salesperson_dashboard"
    sequence="30"
    groups="sales_team.group_sale_salesman"/>
-->
```

**After:**
```xml
<menuitem
    id="menu_grants_training_sales_dashboard"
    name="Sales Dashboard"
    action="grants_training_suite_v19.action_salesperson_dashboard"
    sequence="30"
    groups="sales_team.group_sale_salesman"/>
```

### Change 3: Fix Form View
**File:** `views/salesperson_dashboard_views.xml`

**Issue:** TransientModel had chatter fields (message_follower_ids, activity_ids, message_ids) which are not supported.

**Fix:** Removed chatter div and added Quick Actions buttons instead.

## Why This Happened

During debugging, the view file was simplified to `salesperson_dashboard_views_simple.xml` to isolate loading issues. However:
1. The simple file didn't include the dashboard action
2. The manifest was never updated back to use the full file
3. The menu item remained commented out

## Testing Checklist

After upgrade, verify:
- [ ] Sales Dashboard menu appears under "Intake Management"
- [ ] Clicking it opens the dashboard kanban view
- [ ] KPIs display correctly (Total Contacts, Total Leads, etc.)
- [ ] Buttons in kanban cards work
- [ ] Form view displays all metrics
- [ ] Quick Action buttons work
- [ ] My Contacts menu still works
- [ ] My Leads menu still works

## Related Files

- `models/salesperson_dashboard.py` - Model definition
- `views/salesperson_dashboard_views.xml` - Full views (NOW LOADED)
- `views/salesperson_dashboard_views_simple.xml` - Simplified views (NO LONGER USED)
- `security/ir.model.access.phase2.xml` - Access rights
- `views/menu_views.xml` - Menu structure
- `__manifest__.py` - Module configuration

## Next Steps

If the dashboard loads successfully, we can:
1. Delete `salesperson_dashboard_views_simple.xml` (no longer needed)
2. Add the remaining menus:
   - Pool Utilization Report
   - Sales Rep Performance
3. Test all dashboard functionality with real data

