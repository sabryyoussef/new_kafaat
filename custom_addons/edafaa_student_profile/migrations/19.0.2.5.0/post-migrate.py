def migrate(cr, version):
    """Fill NULL application_status after adding the column."""
    cr.execute(
        """
        UPDATE op_student
           SET application_status = 'under_review'
         WHERE application_status IS NULL
        """
    )
