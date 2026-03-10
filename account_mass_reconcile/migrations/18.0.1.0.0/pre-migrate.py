from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [("account.mass.reconcile", "account_mass_reconcile", "account", "account_id")],
    )
    # Update company_id of account_mass_reconcile (only if null) because if becomes
    # mandatory. First take from journal of the lines (account_mass_reconcile_method)
    # we should have only 1 company since before this version the accounts could only
    # have 1 company
    # else, take first company from account_id
    env.cr.execute("""
        UPDATE account_mass_reconcile amr
        SET company_id = sub.final_company_id
        FROM (
            SELECT
                main.id as main_id,
                COALESCE(
                    (SELECT aj.company_id
                     FROM account_mass_reconcile_method amrm
                     JOIN account_journal aj ON amrm.journal_id = aj.id
                     WHERE amrm.task_id = main.id
                       AND amrm.journal_id IS NOT NULL
                     LIMIT 1),
                    (SELECT MIN(rc.res_company_id)
                     FROM account_account_res_company_rel rc
                     WHERE rc.account_account_id = main.account_id)
                ) as final_company_id
            FROM account_mass_reconcile main
            WHERE main.company_id IS NULL
        ) sub
        WHERE amr.id = sub.main_id
          AND sub.final_company_id IS NOT NULL;
    """)

    env.cr.execute("""
        UPDATE account_mass_reconcile_method
        SET company_id = amr.company_id
        FROM account_mass_reconcile amr
        WHERE amr.id = account_mass_reconcile_method.task_id
        AND account_mass_reconcile_method.company_id IS NULL
    """)

    env.cr.execute("""
        UPDATE mass_reconcile_history
        SET company_id = amr.company_id
        FROM account_mass_reconcile amr
        WHERE amr.id = mass_reconcile_history.mass_reconcile_id
        AND mass_reconcile_history.company_id IS NULL
    """)
