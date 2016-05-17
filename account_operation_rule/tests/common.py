# -*- coding: utf-8 -*-
# Author: Guewen Baconnier
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class AccountOperationTestCase(TransactionCase):

    def setUp(self):
        super(AccountOperationTestCase, self).setUp()
        self.cash_journal = self.env['account.journal'].create({
            'name': 'Unittest Cash journal',
            'code': 'CASH',
            'type': 'cash',
        })

        self.sale_journal = self.env['account.journal'].create({
            'name': 'Unittest Customer Invoices',
            'code': 'INV',
            'type': 'sale',
        })

        receivable_type = self.env['account.account.type'].create({
            'name': 'Receivable',
            'type': 'receivable'
        })

        self.account_receivable = self.env['account.account'].create({
            'name': 'Unittest Account Receivable',
            'user_type_id': receivable_type.id,
            'code': 'TEST101200',
            'reconcile': True,
        })

        income_type = self.env['account.account.type'].create({
            'name': 'Unittest Income',
            'type': 'other'
        })

        self.account_sale = self.env['account.account'].create({
            'name': 'Unittest Account Sale',
            'user_type_id': income_type.id,
            'code': 'TEST200000',
            'reconcile': False,
        })

    def prepare_statement(self, difference,
                          statement_line_currency=None,
                          move_line_currency=None,
                          amount_currency_difference=0):
        """ Prepare a bank statement line and a move line

        The difference is applied on the bank statement line relatively to
        the move line.
        """

        amount = 100
        amount_currency = 120

        statement = self.env['account.bank.statement'].create({
            'name': '/',
            'journal_id': self.cash_journal.id
        })
        line_vals = {
            'name': '001',
            'amount': amount + difference,
            'statement_id': statement.id,
        }
        if statement_line_currency:
            line_vals.update({
                'currency_id': statement_line_currency.id,
                'amount_currency':
                    amount_currency + amount_currency_difference,
            })

        statement_line = self.env['account.bank.statement.line'].create(
            line_vals
        )
        debit_line_vals = {
            'name': '001',
            'account_id': self.account_receivable.id,
            'debit': amount,
        }
        if move_line_currency:
            debit_line_vals.update({
                'currency_id': move_line_currency.id,
                'amount_currency': amount_currency,
            })

        credit_line_vals = {
            'name': '001',
            'account_id': self.account_sale.id,
            'credit': amount,
        }
        if move_line_currency:
            credit_line_vals['currency_id'] = move_line_currency.id

        move = self.env['account.move'].create({
            'journal_id': self.sale_journal.id,
            'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)],
        })

        return statement_line, move.line_ids.filtered(
            lambda l: l.debit != 0.0
        )
