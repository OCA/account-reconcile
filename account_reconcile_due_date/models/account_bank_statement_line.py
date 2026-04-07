# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    date_due = fields.Date(string="Due date")

    def reconcile_bank_line(self):
        res = super().reconcile_bank_line()
        if self.is_reconciled and self.date_due:
            self.move_id.line_ids.date_maturity = self.date_due
        return res
