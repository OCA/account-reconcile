# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def _compute_date_index(self):
        for stmt in self:
            sorted_lines = stmt.line_ids.filtered(lambda line: line._origin.id).sorted(
                'internal_index')
            stmt.first_line_index = sorted_lines[:1].internal_index
            stmt.date = sorted_lines.filtered(lambda l: l.state == 'posted')[-1:].date

    def action_open_statement(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_reconcile_oca.account_bank_statement_action_edit"
        )
        action["res_id"] = self.id
        return action

    def unlink(self):
        for statement in self:
            statement.line_ids.unlink()
        return super(AccountBankStatement, self).unlink()



