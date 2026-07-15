def post_init_hook(env):
    """Fill blank application_status on existing students after S2 upgrade."""
    students = env['op.student'].search([('application_status', '=', False)])
    if students:
        students.write({'application_status': 'under_review'})
