# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"

    def _apply_conditions(self, query, params):
        query, params = super()._apply_conditions(query, params)
        if self.rule_type == "invoice_matching":
            query += " AND account.exclude_bank_reconcile IS NOT TRUE"
        return query, params
