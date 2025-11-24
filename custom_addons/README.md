# Custom Addons Directory

This directory contains all custom Odoo modules for the project.

## Module Structure

All Odoo custom modules are organized in this `custom_addons` folder. This follows the standard Odoo convention for organizing custom modules.

## Modules Included

1. **grants_training_suite_v19** - Training center management system (Odoo 19)
   - Grant intake to certification workflow
   - Contact Pool Architecture (Phase 1)
   - eLearning integration
   - Student portal

2. **hr_employee_enhance** - HR Employee enhancements
   - Employee code sequences
   - Additional employee fields

3. **hr_reward_warning** - HR Reward and Warning system
   - Employee announcements
   - Reward and warning management

4. **itech_hr_petty_cash_report** - Petty cash reporting for HR
   - Petty cash report generation
   - HR integration

5. **petty_cash_management** - Petty cash management system
   - Petty cash request and approval workflow
   - Cash management features

6. **petty_expenses** - Petty expenses module
   - Expense tracking
   - Integration with petty cash

7. **web_environment_ribbon** - Web environment ribbon indicator
   - Visual indicator for environment (dev/staging/prod)
   - Environment-specific configurations

8. **wm_journal_entry_report** - Journal entry reporting
   - Custom journal entry reports
   - Accounting integration

## Odoo Configuration

To use these modules, add this path to your Odoo configuration file (`odoo.conf`):

```ini
addons_path = /path/to/odoo/addons,/path/to/odoo/enterprise,/home/sabry3/Downloads/kafaat-main/custom_addons
```

Or if you're using a relative path from your Odoo installation:

```ini
addons_path = addons,enterprise,../kafaat-main/custom_addons
```

## Installation

1. Ensure the `custom_addons` directory is in your Odoo addons path
2. Update the module list in Odoo (Settings > Apps > Update Apps List)
3. Install the desired modules from the Apps menu

## Notes

- All modules follow Odoo module structure conventions
- Each module has its own `__manifest__.py` file
- Security rules are defined in each module's `security/` directory
- Views are organized in each module's `views/` directory

