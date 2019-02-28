# Copyright 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, timedelta

from odoo.tests.common import SavepointCase, at_install, post_install


@at_install(False)
@post_install(True)
class TestEarlyPaymentDiscountRule(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Customer Partner
        cls.partner = cls.env['res.partner'].with_context(
            tracking_disable=True).create({
                'name': 'Customer partner',
            })

        cls.rule_model = cls.env['account.reconcile.rule']
        # Delete existing rules
        cls.rule_model.search([]).unlink()

        # Creation operation template and rule
        cls.operation = cls.env['account.reconcile.model'].create({
            'name': 'Unittest Early Payment Discount',
            'label': 'Rounding',
            'amount_type': 'percentage',
            'amount': 100.0,
        })
        cls.reconciliation_rule = cls.rule_model.create({
            'name': 'Unittest Early Payment Discount',
            'rule_type': 'early_payment_discount',
            'operations': [(6, 0, (cls.operation.id, ))],
            'sequence': 1,
        })
        # Accounts creation
        account_model = cls.env['account.account']
        cls.account_early_payment = account_model.create({
            'name': 'Unittest Account Early Payment Discount',
            'user_type_id':
                cls.env.ref('account.data_account_type_expenses').id,
            'code': 'TEST4090',
            'reconcile': False,
        })
        cls.account_sale = account_model.create({
            'name': 'Unittest Account Sale',
            'user_type_id':
                cls.env.ref('account.data_account_type_other_income').id,
            'code': 'TEST200000',
            'reconcile': False,
        })
        cls.account_customer = account_model.create({
            'code': 'TEST1100',
            'name': 'Customer account',
            'user_type_id':
                cls.env.ref('account.data_account_type_receivable').id,
            'reconcile': True,
        })
        cls.cash_journal = cls.env['account.journal'].create({
            'name': 'Unittest Cash journal',
            'code': 'CASH',
            'type': 'cash',
        })
        cls.sale_journal = cls.env['account.journal'].create({
            'name': 'Unittest Customer Invoices',
            'code': 'INV',
            'type': 'sale',
        })
        # Early payment discount payment term.
        cls.payment_term = cls.env['account.payment.term'].create({
            'name': '10 days 2% discount',
            'early_payment_discount': True,
            'epd_nb_days': 10,
            'epd_discount': 2,
        })
        # Product and invoice with price = 1000
        product_test = cls.env['product.product'].create({
            'name': 'Unittest product',
        })
        cls.date_invoice = date(2016, 5, 10)
        cls.invoice = cls.env['account.invoice'].create({
            'name': "Test Customer Invoice",
            'date_invoice': cls.date_invoice,
            'account_id': cls.account_customer.id,
            'partner_id': cls.partner.id,
            'payment_term_id': cls.payment_term.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': product_test.id,
                    'account_id': cls.account_sale.id,
                    'quantity': 1.0,
                    'name': 'Unittest product 4',
                    'price_unit': 1000.00,
                })
            ]
        })
        # Create move
        debit_line_vals = {
            'name': '001',
            'invoice_id': cls.invoice.id,
            'account_id': cls.account_customer.id,
            'debit': 1000.0,
        }
        credit_line_vals = {
            'name': '001',
            'account_id': cls.account_sale.id,
            'credit': 1000.0,
        }
        cls.move = cls.env['account.move'].create({
            'journal_id': cls.sale_journal.id,
            'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)],
        })
        cls.debit_move = cls.move.line_ids.filtered(
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
        self.assertEqual(self.reconciliation_rule, rule)

        statement = self.create_statement_line(980, delta_days=10)
        rule = self.rule_model.find_first_rule(statement, self.debit_move)
        self.assertEqual(self.reconciliation_rule, rule)

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
        self.assertEqual(self.reconciliation_rule, rule)

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
        self.reconciliation_rule.rule_type = "rounding"

        statement = self.create_statement_line(990)
        rule = self.rule_model.find_first_rule(statement, self.debit_move)
        self.assertFalse(rule)
