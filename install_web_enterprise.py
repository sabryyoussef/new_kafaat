#!/usr/bin/env python3
"""
Script to install web_enterprise module in Odoo 19
Run this inside the Odoo container with proper database connection
"""
import sys
import os

# Add Odoo to path
sys.path.insert(0, '/usr/lib/python3/dist-packages')

import odoo
from odoo import api, SUPERUSER_ID

def install_web_enterprise(db_name='kafaat19'):
    """Install web_enterprise module"""
    try:
        # Parse configuration
        odoo.tools.config.parse_config([
            '-d', db_name,
            '--db_host=db',
            '--db_user=odoo',
            '--db_password=odoo',
            '--db_port=5432',
            '--addons-path=/mnt/extra-addons,/mnt/enterprise-addons,/usr/lib/python3/dist-packages/odoo/addons',
            '--stop-after-init'
        ])
        
        # Initialize registry
        registry = odoo.registry(db_name)
        
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            Module = env['ir.module.module']
            
            # Search for web_enterprise module
            web_enterprise = Module.search([('name', '=', 'web_enterprise')], limit=1)
            
            if not web_enterprise:
                print(f"ERROR: web_enterprise module not found in addons path")
                print("Available modules with 'web' in name:")
                web_modules = Module.search([('name', 'like', 'web%')])
                for mod in web_modules[:10]:
                    print(f"  - {mod.name} ({mod.state})")
                return False
            
            print(f"Found web_enterprise module. Current state: {web_enterprise.state}")
            
            if web_enterprise.state == 'installed':
                print("web_enterprise is already installed!")
                return True
            
            # Install the module
            print("Installing web_enterprise...")
            web_enterprise.button_immediate_install()
            cr.commit()
            
            # Verify installation
            web_enterprise.refresh()
            if web_enterprise.state == 'installed':
                print("✅ web_enterprise installed successfully!")
                return True
            else:
                print(f"❌ Installation may have failed. Current state: {web_enterprise.state}")
                return False
                
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    db_name = sys.argv[1] if len(sys.argv) > 1 else 'kafaat19'
    success = install_web_enterprise(db_name)
    sys.exit(0 if success else 1)

