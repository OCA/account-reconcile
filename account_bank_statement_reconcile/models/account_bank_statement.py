# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    @api.multi
    def action_open_reconcile(self):
        return {
            "type": "ir.actions.client",
            "tag": "bank_statement_reconciliation_view",
            "context": {
                "statement_ids": self.ids,
                "company_ids": self.mapped("company_id").ids,
            },
        }

    @api.multi
    def action_unreconcile(self):
        self.mapped("line_ids").button_cancel_reconciliation()

    @api.multi
    def action_reset_to_new(self):
        self.write({
            "state": "open",
        })

    @api.multi
    def action_validate(self):
        self.button_confirm_bank()

    @api.multi
    def action_confirm_balance_and_validate(self):
        for statement in self:
            statement.balance_end_real = statement.balance_end
        self.button_confirm_bank()
