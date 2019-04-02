# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import float_repr, float_round
from odoo import models


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def get_reconciliation_proposition(self, excluded_ids=None):
        """Search first if there are PoS session statements with the
        corresponding amount and no reconcile for proposing this.
        """
        # Get amount without float rounding problem
        amount = self.amount_currency or self.amount
        company_currency = self.journal_id.company_id.currency_id
        st_line_currency = self.currency_id or self.journal_id.currency_id
        precision = (
            st_line_currency.decimal_places or company_currency.decimal_places
        )
        amount = float_repr(
            float_round(amount, precision_digits=precision),
            precision_digits=precision,
        )
        # Search statements with that amount
        statements = self.env['account.bank.statement'].search([
            ('pos_session_id', '!=', False),
            ('all_lines_reconciled', '=', False),
            ('total_entry_encoding', '=', amount),
        ])
        for statement in statements:
            # Discard statements with some reconciled items
            journal = statement.journal_id
            proposition = statement.move_line_ids.filtered(lambda x: (
                x.account_id == journal.default_credit_account_id and
                x.credit > 0
            )) + statement.move_line_ids.filtered(lambda x: (
                x.account_id == journal.default_debit_account_id and
                x.debit > 0
            ))
            if all([not x.reconciled or not x.statement_line_id
                    for x in proposition]):
                return proposition
        return super().get_reconciliation_proposition(
            excluded_ids=excluded_ids,
        )
