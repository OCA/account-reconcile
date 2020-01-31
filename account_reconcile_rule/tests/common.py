# Author: Guewen Baconnier
# Copyright 2014 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class AccountReconciliationModelTestCase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.reconcile_model_obj = cls.env['account.reconcile.model']
        cls.rule_obj = cls.env['account.reconcile.rule']
        cls.journal_obj = cls.env['account.journal']
        cls.account_type_obj = cls.env['account.account.type']
        cls.account_obj = cls.env['account.account']
        cls.cash_journal = cls.journal_obj.create({
            'name': 'Unittest Cash journal',
            'code': 'CASH',
            'type': 'cash',
        })
        cls.sale_journal = cls.journal_obj.create({
            'name': 'Unittest Customer Invoices',
            'code': 'INV',
            'type': 'sale',
        })
        receivable_type = cls.account_type_obj.create({
            'name': 'Receivable',
            'type': 'receivable'
        })
        cls.account_receivable = cls.account_obj.create({
            'name': 'Unittest Account Receivable',
            'user_type_id': receivable_type.id,
            'code': 'TEST101200',
            'reconcile': True,
        })
        income_type = cls.account_type_obj.create({
            'name': 'Unittest Income',
            'type': 'other'
        })
        cls.account_sale = cls.account_obj.create({
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
