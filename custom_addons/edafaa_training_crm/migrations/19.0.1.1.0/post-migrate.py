def migrate(cr, version):
    cr.execute("""
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'crm_team' AND column_name = 'lead_target'
    """)
    if not cr.fetchone():
        return
    cr.execute("""
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'crm_team' AND column_name = 'pipeline_target'
    """)
    if cr.fetchone():
        cr.execute("""
            UPDATE crm_team
            SET pipeline_target = lead_target
            WHERE COALESCE(pipeline_target, 0) = 0
              AND COALESCE(lead_target, 0) <> 0
        """)
        return
    cr.execute('ALTER TABLE crm_team RENAME COLUMN lead_target TO pipeline_target')
