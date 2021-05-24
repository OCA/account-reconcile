# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.tools.misc import format_date, parse_date


class AccountReconciliation(models.AbstractModel):
    _inherit = "account.reconciliation.widget"

    @api.model
    def _get_statement_line(self, st_line):
        data = super()._get_statement_line(st_line)
        data["date_due"] = format_date(self.env, st_line.date_due)
        return data

    @api.model
    def process_bank_statement_line(self, st_line_ids, data):
        res = super().process_bank_statement_line(st_line_ids, data)
        AccountMove = self.env["account.move"]
        st_line_Move = self.env["account.bank.statement.line"]
        key = 0
        for move in res["moves"]:
            if "date_due" in data[key] and data[key]["date_due"]:
                move_record = AccountMove.browse(move)
                st_line = st_line_Move.browse(st_line_ids[key])
                st_line.date_due = parse_date(self.env, data[key]["date_due"])
                move_record.line_ids.date_maturity = st_line.date_due
            key += 1
        return res
