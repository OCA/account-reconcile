# Copyright 2025 Victor M.M. Torres, Tecnativa SL
# Licence LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).
from odoo import models


class AccountReconcileModelLine(models.Model):
    _inherit = "account.reconcile.model.line"

    def _get_write_off_move_line_dict(self, balance, currency):
        self.ensure_one()
        return {
            "name": self.label,
            "balance": balance,
            "debit": balance > 0 and balance or 0,
            "credit": balance < 0 and -balance or 0,
            "account_id": self.account_id.id,
            "currency_id": currency.id,
            "analytic_distribution": self.analytic_distribution,
            "reconcile_model_id": self.model_id.id,
            "journal_id": self.journal_id.id,
            "tax_ids": [],
        }
