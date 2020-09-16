# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.osv import expression


class AccountReconciliation(models.AbstractModel):
    _inherit = "account.reconciliation.widget"

    @api.model
    def _domain_move_lines_for_reconciliation(
        self,
        st_line,
        aml_accounts,
        partner_id,
        excluded_ids=None,
        search_str=False,
        mode="rp",
    ):
        domain = super()._domain_move_lines_for_reconciliation(
            st_line,
            aml_accounts,
            partner_id,
            excluded_ids=excluded_ids,
            search_str=search_str,
            mode=mode,
        )
        domain = expression.AND(
            [domain, [("account_id.exclude_bank_reconcile", "!=", True)]]
        )
        # Extract from context allowed accounts defined in Journal, if any
        journal_id = st_line.journal_id
        account_reconciliation_ids = journal_id.account_reconciliation_ids
        if account_reconciliation_ids:
            domain = expression.AND(
                [domain, [("account_id", "in", account_reconciliation_ids.ids)]]
            )
        return domain
