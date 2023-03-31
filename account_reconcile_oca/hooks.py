def post_init_hook(cr, registry):
    cr.execute(
        """
        UPDATE account_bank_statement_line
        SET reconcile_mode = 'edit'
        WHERE is_reconciled
        """
    )
