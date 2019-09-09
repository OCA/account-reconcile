# Copyright 2015 Therp BV (<http://therp.nl>)
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def get_possible_payment_orders_for_statement_line(self):
        """Find orders that might be candidates for matching a statement
        line.
        """
        return self.env['account.payment.order'].search([
            ('total_company_currency', '=', self.amount),
            ('state', 'in', ['done', 'uploaded']),
        ])

    def prepare_proposition_from_orders(self, orders, excluded_ids=None):
        """Fill with the expected format the reconciliation proposition
        for the given statement line and possible payment orders.
        """
        aml_obj = self.env['account.move.line']
        for order in orders:
            reconciled_lines = aml_obj.search([
                ('bank_payment_line_id', 'in', order.bank_line_ids.ids)
            ])
            elegible_lines = (
                reconciled_lines.mapped('move_id.line_ids') -
                reconciled_lines - aml_obj.browse(excluded_ids)
            ).filtered(lambda x: not x.reconciled)
            if elegible_lines:
                return elegible_lines
        return aml_obj

    def get_reconciliation_proposition(self, excluded_ids=None):
        """See if we find a payment order that matches our line. If yes,
        return all unreconciled lines from there"""
        orders = self.get_possible_payment_orders_for_statement_line()
        reconcile_lines = self.prepare_proposition_from_orders(
            orders, excluded_ids=excluded_ids)
        if reconcile_lines:
            return reconcile_lines
        return super(AccountBankStatementLine, self)\
            .get_reconciliation_proposition(excluded_ids=excluded_ids)
