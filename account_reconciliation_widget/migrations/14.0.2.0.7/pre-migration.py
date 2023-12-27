# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Mitigate a bit the problem on past reconciled invoices, for being available
    to be reconciled again if we press "Revert reconciliation" on the statement line.

    This doesn't cover other AR/AP lines, but at least we keep data consistent for
    these ones.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET statement_line_id = NULL, statement_id = NULL
        FROM account_move am WHERE am.id = aml.move_id
        AND aml.statement_line_id IS NOT NULL
        AND am.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
        """,
    )
