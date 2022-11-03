# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2021 Tecnativa - Alexandre D. Díaz
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
    def update_bank_statement_line_due_date(self, move_ids, st_line_ids, dates):
        """'move_ids', 'st_line_ids' and 'dates' must have the same length"""
        account_move_obj = self.env["account.move"]
        st_line_move_obj = self.env["account.bank.statement.line"]
        for index, move_id in enumerate(move_ids):
            move_record = account_move_obj.browse(move_id)
            st_line = st_line_move_obj.browse(st_line_ids[index])
            st_line.date_due = parse_date(self.env, dates[index])
            if st_line.date_due:
                move_record.line_ids.date_maturity = st_line.date_due
