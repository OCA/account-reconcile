# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.tools.safe_eval import safe_eval


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def action_open_statement(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_reconcile_oca.account_bank_statement_action_edit"
        )
        action["res_id"] = self.id
        return action

    def action_open_statement_lines(self):
        """Open in reconciling view directly"""
        self.ensure_one()
        if not self:
            return {}
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_reconcile_oca.action_bank_statement_line_reconcile"
        )
        action["domain"] = [("statement_id", "=", self.id)]
        action["context"] = safe_eval(
            action["context"], locals_dict={"active_id": self._context.get("active_id")}
        )
        return action
