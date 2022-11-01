# Copyright 2022 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    reconcile_mode = fields.Selection(
        [("edit", "Edit Move"), ("keep", "Keep Suspense Accounts")],
        default="edit",
        required=True,
    )

    def action_open_reconcile_to_check(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_reconcile_oca.action_bank_statement_line_reconcile"
        )
        action["domain"] = [("id", "=", self.to_check_ids().ids)]
        return action

    def get_rainbowman_message(self):
        self.ensure_one()
        if self.get_journal_dashboard_datas()["number_to_reconcile"] > 0:
            return False
        return _("Well done! Everything has been reconciled")
