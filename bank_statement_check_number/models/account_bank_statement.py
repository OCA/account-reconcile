# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    check_number = fields.Char(
        copy=False,
        index=True,
    )

    @api.model
    def _prepare_move_line_default_vals(self, counterpart_account_id=None):
        move_lines = super()._prepare_move_line_default_vals(counterpart_account_id)
        for move_line in move_lines:
            move_line.update({"check_number": self.check_number})
        return move_lines
