# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    def action_reconcile_manually(self):
        if not self:
            return {}
        accounts = self.mapped("account_id")
        if len(accounts) > 1:
            raise ValidationError(
                _("You can only reconcile journal items belonging to the same account.")
            )
        partner = self.mapped("partner_id")
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_reconcile_oca.account_account_reconcile_act_window"
        )
        action["domain"] = [("account_id", "=", self.mapped("account_id").id)]
        if len(partner) == 1 and self.account_id.account_type in [
            "asset_receivable",
            "liability_payable",
        ]:
            action["domain"] += [("partner_id", "=", partner.id)]
        action["context"] = self.env.context.copy()
        action["context"]["default_account_move_lines"] = self.filtered(
            lambda r: not r.reconciled
        ).ids
        return action
