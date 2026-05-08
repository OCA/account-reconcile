# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def action_reconcile_manually(self):
        # Override the method from account_reconcile_oca
        # to open the new wizard instead of the conciliation widget.
        wizard = (
            self.env["account.manual.reconcile.wizard"]
            .with_context(active_model="account.move.line", active_ids=self.ids)
            .create({})
        )
        if not wizard.need_write_off:
            wizard.allow_partial_reconcile = True
            return wizard.action_reconcile()
        return wizard._get_records_action(
            target="new", name=self.env._("Reconciliation")
        )
