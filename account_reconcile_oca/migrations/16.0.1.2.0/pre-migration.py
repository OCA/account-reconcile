from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(
        env.cr, "account_bank_statement_line", "reconcile_data"
    ):
        return  # coming directly from v15, so reconcile_data doesn't exist
    # Due to the big change we did, we need to loose how data is stored
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_bank_statement_line
            SET reconcile_data = NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            DELETE FROM account_account_reconcile_data
        """,
    )
