# Copyright 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import api, fields, models


class AccountReconcileRule(models.Model):
    _inherit = 'account.reconcile.rule'

    rule_type = fields.Selection(
        selection_add=[('early_payment_discount', 'Early Payment Discount')],
    )

    @api.multi
    def _is_valid_early_payment_discount(self, statement_line, move_lines,
                                         balance):
        """Return True if *move_lines* are linked to only one invoice
        with a payment term which has an early payment discount
        and if *balance* and the *statement_line* date match the
        early payment discount rules.

        :type statement_line: AccountBankStatementLine
        :type move_lines: stock_move
        :type balance: float
        :rtype: bool
        """

        if not move_lines or balance >= 0:
            return False
        else:
            invoice = move_lines.mapped('invoice_id')

            if len(invoice) != 1:
                return False
            elif not invoice.payment_term_id.early_payment_discount:
                return False
            else:
                return self._check_early_payment_discount(
                    statement_line, invoice, balance
                )

    @api.multi
    def _check_early_payment_discount(self, statement_line, invoice,
                                      balance):
        """ Return True if *balance* and the *statement_line* date match the
        early payment discount rules for *invoice*.

        :type statement_line: AccountBankStatementLine
        :type invoice: AccountInvoice
        :type balance: float
        :rtype: bool
        """
        payment_term = invoice.payment_term_id

        max_date = fields.Date.from_string(invoice.date_invoice) + timedelta(
            days=payment_term.epd_nb_days
        )

        if fields.Date.from_string(statement_line.date) > max_date:
            return False

        percent = payment_term.epd_discount / 100.0
        discount_balance = invoice.amount_total * percent

        if payment_term.epd_tolerance:
            discount_balance += payment_term.epd_tolerance

        return self._between_with_bounds(
            # Balance is negative in our case
            0, -balance, discount_balance, statement_line.currency_for_rules()
        )

    @api.multi
    def is_valid(self, statement_line, move_lines, balance):
        """ Override account.operation.rule is_valid for early_payment_discount
        case
        """
        if self.rule_type == 'early_payment_discount':
            return self._is_valid_early_payment_discount(
                statement_line, move_lines, balance
            )
        else:
            return super().is_valid(statement_line, move_lines, balance)
