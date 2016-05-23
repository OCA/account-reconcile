# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date, timedelta

from openerp.tests import common


class TestEarlyPaymentDiscountRule(common.TransactionCase):

    def setUp(self):
        super(TestEarlyPaymentDiscountRule, self).setUp()

        # Customer Partner
        self.partner = self.env['res.partner'].create({
            'name': 'Customer partner',
        })

        self.rule_model = self.env['account.operation.rule']
        # Delete existing rules
        self.rule_model.search([]).unlink()

        # Creation operation template and rule
        self.operation = self.env['account.operation.template'].create({
            'name': 'Unittest Early Payment Discount',
            'label': 'Rounding',
            'amount_type': 'percentage',
            'amount': 100.0,
        })

        self.operation_rule = self.rule_model.create({
            'name': 'Unittest Early Payment Discount',
            'rule_type': 'early_payment_discount',
            'operations': [(6, 0, (self.operation.id, ))],
            'sequence': 1,
        })

        # Accounts creation
        account_model = self.env['account.account']

        self.account_early_payment = account_model.create({
            'name': 'Unittest Account Early Payment Discount',
            'user_type_id': self.ref('account.data_account_type_expenses'),
            'code': 'TEST4090',
            'reconcile': False,
        })

        self.account_sale = account_model.create({
            'name': 'Unittest Account Sale',
            'user_type_id': self.ref('account.data_account_type_other_income'),
            'code': 'TEST200000',
            'reconcile': False,
        })

        self.account_customer = account_model.create({
            'code': 'TEST1100',
            'name': 'Customer account',
            'user_type_id': self.ref('account.data_account_type_receivable'),
            'reconcile': True,
        })

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

        # Early payment discount payment term.
        self.payment_term = self.env['account.payment.term'].create({
            'name': '10 days 2% discount',
            'early_payment_discount': True,
            'epd_nb_days': 10,
            'epd_discount': 2,
        })

        # Product and invoice with price = 1000
        product_test = self.env['product.product'].create({
            'name': 'Unittest product',
        })

        self.date_invoice = date(2016, 5, 10)
        self.invoice = self.env['account.invoice'].create({
            'name': "Test Customer Invoice",
            'date_invoice': self.date_invoice,
            'account_id': self.account_customer.id,
            'partner_id': self.partner.id,
            'payment_term_id': self.payment_term.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': product_test.id,
                    'account_id': self.account_sale.id,
                    'quantity': 1.0,
                    'name': 'Unittest product 4',
                    'price_unit': 1000.00,
                })
            ]
        })

        # Create move
        debit_line_vals = {
            'name': '001',
            'invoice_id': self.invoice.id,
            'account_id': self.account_customer.id,
            'debit': 1000.0,
        }
        credit_line_vals = {
            'name': '001',
            'account_id': self.account_sale.id,
            'credit': 1000.0,
        }
        self.move = self.env['account.move'].create({
            'journal_id': self.sale_journal.id,
            'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)],
        })

        self.debit_move = self.move.line_ids.filtered(
            lambda l: l.debit != 0.0
        )

    def create_statement_line(self, amount, delta_days=0):
        statement = self.env['account.bank.statement'].create({
            'name': '/',
            'journal_id': self.cash_journal.id,
        })

        return self.env['account.bank.statement.line'].create({
            'statement_id': statement.id,
            'name': '001',
            'amount': amount,
            'date': self.date_invoice + timedelta(days=delta_days),
        })

    def test_early_payment_discount(self):
        # Balance = 0
        statement = self.create_statement_line(1000)
        rule = self.rule_model.find_first_rule(statement, self.debit_move)
        self.assertFalse(rule)

        # Balance > 0
        statement = self.create_statement_line(1100)
        rule = self.rule_model.find_first_rule(statement, self.debit_move)
        self.assertFalse(rule)

        # good date and amount in discount
        statement = self.create_statement_line(990, delta_days=5)
        rule = self.rule_model.find_first_rule(statement, self.debit_move)
        self.assertEqual(self.operation_rule, rule)

        statement = self.create_statement_line(980, delta_days=10)
        rule = self.rule_model.find_first_rule(statement, self.debit_move)
        self.assertEqual(self.operation_rule, rule)

        # Good date but amount to low
        statement = self.create_statement_line(970, delta_days=5)
        rule = self.rule_model.find_first_rule(statement, self.debit_move)
        self.assertFalse(rule)

        # Amount good but date too late
        statement = self.create_statement_line(985, delta_days=11)
        rule = self.rule_model.find_first_rule(statement, self.debit_move)
        self.assertFalse(rule)

    def test_tolerance(self):
        self.payment_term.epd_discount = 2.25
        self.payment_term.epd_tolerance = 0.5

        statement = self.create_statement_line(977)
        rule = self.rule_model.find_first_rule(statement, self.debit_move)
        self.assertEqual(self.operation_rule, rule)

        self.payment_term.epd_tolerance = 0.4
        statement = self.create_statement_line(977)
        rule = self.rule_model.find_first_rule(statement, self.debit_move)
        self.assertFalse(rule)

    def test_no_invoice(self):
        self.debit_move.invoice_id = False

        statement = self.create_statement_line(990)
        rule = self.rule_model.find_first_rule(statement, self.debit_move)
        self.assertFalse(rule)

    def test_no_discount_payment_term(self):
        self.payment_term.early_payment_discount = False

        statement = self.create_statement_line(990)
        rule = self.rule_model.find_first_rule(statement, self.debit_move)
        self.assertFalse(rule)

    def test_bad_rule_type(self):
        self.operation_rule.rule_type = "rounding"

        statement = self.create_statement_line(990)
        rule = self.rule_model.find_first_rule(statement, self.debit_move)
        self.assertFalse(rule)
