# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    @api.multi
    def action_open_reconcile(self):
        return {
            "type": "ir.actions.client",
            "tag": "bank_statement_reconciliation_view",
            "context": {
                "statement_ids": self.mapped("statement_id").ids,
                "company_ids": self.mapped("company_id").ids,
            },
        }

    @api.multi
    def action_unreconcile(self):
        self.button_cancel_reconciliation()
