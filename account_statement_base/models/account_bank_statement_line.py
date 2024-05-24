# Copyright 2024 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def action_open_journal_entry(self):
        self.ensure_one()
        if not self:
            return {}
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_line_form"
        )
        res = self.env.ref("account.view_move_form", False)
        result["views"] = [(res and res.id or False, "form")]
        result["res_id"] = self.move_id.id
        return result
