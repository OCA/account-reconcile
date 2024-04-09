# Copyright 2024 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    @api.depends("line_ids.internal_index", "line_ids.state")
    def _compute_date_index(self):
        for stmt in self:
            sorted_lines = stmt.line_ids.filtered(lambda l: l.internal_index).sorted(
                "internal_index"
            )
            stmt.first_line_index = sorted_lines[:1].internal_index
            stmt.date = sorted_lines.filtered(lambda l: l.state == "posted")[-1:].date
