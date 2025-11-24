#!/usr/bin/env python3
import psycopg2

# Connect to database
conn = psycopg2.connect(
    dbname="odoo19",
    user="odoo19",
    password="odoo19",
    host="localhost"
)
cur = conn.cursor()

# Check if action exists in ir_act_window
print("=" * 80)
print("Checking ir.actions.act_window for salesperson dashboard...")
print("=" * 80)
cur.execute("""
    SELECT id, name, res_model, view_mode 
    FROM ir_act_window 
    WHERE res_model = 'salesperson.dashboard' OR name ILIKE '%sales dashboard%'
""")
actions = cur.fetchall()
if actions:
    print(f"Found {len(actions)} action(s):")
    for action in actions:
        print(f"  ID: {action[0]}, Name: {action[1]}, Model: {action[2]}, View Mode: {action[3]}")
else:
    print("  ❌ NO ACTIONS FOUND for salesperson.dashboard")

# Check if external ID exists
print("\n" + "=" * 80)
print("Checking ir.model.data for external IDs...")
print("=" * 80)
cur.execute("""
    SELECT module, name, model, res_id 
    FROM ir_model_data 
    WHERE name ILIKE '%salesperson%dashboard%' OR name = 'action_salesperson_dashboard'
""")
external_ids = cur.fetchall()
if external_ids:
    print(f"Found {len(external_ids)} external ID(s):")
    for ext_id in external_ids:
        print(f"  Module: {ext_id[0]}, Name: {ext_id[1]}, Model: {ext_id[2]}, Res ID: {ext_id[3]}")
else:
    print("  ❌ NO EXTERNAL IDs FOUND")

# Check if model exists
print("\n" + "=" * 80)
print("Checking ir.model for salesperson.dashboard model...")
print("=" * 80)
cur.execute("""
    SELECT id, model, name, transient 
    FROM ir_model 
    WHERE model = 'salesperson.dashboard'
""")
models = cur.fetchall()
if models:
    print(f"Found model:")
    for model in models:
        print(f"  ID: {model[0]}, Model: {model[1]}, Name: {model[2]}, Transient: {model[3]}")
else:
    print("  ❌ MODEL NOT FOUND in ir.model")

cur.close()
conn.close()
