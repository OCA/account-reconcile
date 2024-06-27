# Copyright 2024 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------
    @api.depends("line_ids.internal_index", "line_ids.state")
    def _compute_date_index(self):
        for stmt in self:
            # When we create a new statement line for existing statement,
            # internal_index field of line can be False
            # And we can not sort str and bool type (python error)
            # sort only line with internal_index != False to avoid bug when sort value from
            # different type
            sorted_lines = stmt.line_ids.filtered(lambda l: l.internal_index).sorted(
                "internal_index"
            )
            if not sorted_lines:
                sorted_lines = stmt.line_ids
            stmt.first_line_index = sorted_lines[:1].internal_index
            stmt.date = sorted_lines.filtered(lambda l: l.state == "posted")[-1:].date
