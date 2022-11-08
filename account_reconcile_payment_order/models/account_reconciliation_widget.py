# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class AccountReconciliationWidget(models.AbstractModel):
    _inherit = "account.reconciliation.widget"

    @api.model
    def _get_possible_payment_orders_for_statement_line(self, st_line):
        """Find orders that might be candidates for matching a statement
        line.
        """
        return self.env["account.payment.order"].search(
            [
                ("total_company_currency", "=", st_line.amount),
                ("state", "in", ["done", "uploaded"]),
            ]
        )

    @api.model
    def _get_reconcile_lines_from_order(self, st_line, order, excluded_ids=None):
        """Return lines to reconcile our statement line with."""
        aml_obj = self.env["account.move.line"]
        lines = aml_obj
        for payment in order.payment_ids:
            lines |= payment.move_id.line_ids.filtered(
                lambda x: x.account_id != payment.destination_account_id
                and x.partner_id == payment.partner_id
            )
        return (lines - aml_obj.browse(excluded_ids)).filtered(
            lambda x: not x.reconciled
        )

    def _prepare_proposition_from_orders(self, st_line, orders, excluded_ids=None):
        """Fill with the expected format the reconciliation proposition
        for the given statement line and possible payment orders.
        """
        target_currency = (
            st_line.currency_id
            or st_line.journal_id.currency_id
            or st_line.journal_id.company_id.currency_id
        )
        for order in orders:
            elegible_lines = self._get_reconcile_lines_from_order(
                st_line,
                order,
                excluded_ids=excluded_ids,
            )
            if elegible_lines:
                return self._prepare_move_lines(
                    elegible_lines,
                    target_currency=target_currency,
                    target_date=st_line.date,
                )
        return []

    def get_bank_statement_line_data(self, st_line_ids, excluded_ids=None):
        res = super().get_bank_statement_line_data(
            st_line_ids,
            excluded_ids=excluded_ids,
        )
        st_line_obj = self.env["account.bank.statement.line"]
        for line_vals in res.get("lines", []):
            st_line = st_line_obj.browse(line_vals["st_line"]["id"])
            orders = self._get_possible_payment_orders_for_statement_line(st_line)
            proposition_vals = self._prepare_proposition_from_orders(
                st_line,
                orders,
                excluded_ids=excluded_ids,
            )
            if proposition_vals:
                line_vals["reconciliation_proposition"] = proposition_vals
        return res
