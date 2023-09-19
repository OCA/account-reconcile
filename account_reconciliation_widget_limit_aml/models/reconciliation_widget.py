# Copyright 2023 Valentin Vinagre <valentin.vinagre@sygel.es>
# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
            st_line, aml_accounts, partner_id, excluded_ids, search_str, mode
        )
        if (
            st_line.company_id.account_bank_reconciliation_start_all_aml
            and st_line.company_id.account_bank_reconciliation_start
        ):
            domain = expression.AND(
                [
                    domain,
                    [
                        (
                            "date",
                            ">=",
                            st_line.company_id.account_bank_reconciliation_start,
                        )
                    ],
                ]
            )
        return domain
