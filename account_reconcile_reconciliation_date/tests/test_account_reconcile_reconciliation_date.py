# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.account.tests.account_test_classes import AccountingTestCase
import time


class TestAccountReconcileReconciliationDate(AccountingTestCase):
    def setUp(self):
        super(TestAccountReconcileReconciliationDate, self).setUp()
        self.register_payments_model = self.env['account.register.payments'].\
            with_context(active_model='account.invoice')
        self.payment_model = self.env['account.payment']
        self.invoice_model = self.env['account.invoice']
        self.invoice_line_model = self.env['account.invoice.line']
        self.acc_bank_stmt_model = self.env['account.bank.statement']
        self.acc_bank_stmt_line_model = self.\
            env['account.bank.statement.line']

        self.partner_agrolait = self.env.ref("base.res_partner_2")
        self.partner_china_exp = self.env.ref("base.res_partner_3")
        self.currency_chf_id = self.env.ref("base.CHF").id
        self.currency_usd_id = self.env.ref("base.USD").id
        self.currency_eur_id = self.env.ref("base.EUR").id

        company = self.env.ref('base.main_company')
        self.cr.\
            execute("UPDATE res_company SET currency_id = %s WHERE id = %s",
                    [self.currency_eur_id, company.id])
        self.product = self.env.ref("product.product_product_4")
        self.payment_method_manual_in = self.env.\
            ref("account.account_payment_method_manual_in")
        self.payment_method_manual_out = self.env.\
            ref("account.account_payment_method_manual_out")

        self.account_receivable = self.env['account.account'].\
            search([('user_type_id', '=', self.
                   env.ref('account.data_account_type_receivable').id)],
                   limit=1)
        self.account_payable = self.env['account.account'].\
            search([('user_type_id', '=', self.env.
                   ref('account.data_account_type_payable').id)], limit=1)
        self.account_revenue = self.env['account.account'].\
            search([('user_type_id', '=', self.env.
                     ref('account.data_account_type_revenue').id)], limit=1)

        self.bank_journal_euro = self.env['account.journal'].\
            create({'name': 'Bank', 'type': 'bank', 'code': 'BNK67'})
        self.account_eur = self.bank_journal_euro.default_debit_account_id

        self.bank_journal_usd = self.env['account.journal'].\
            create({'name': 'Bank US',
                    'type': 'bank',
                    'code': 'BNK68',
                    'currency_id': self.currency_usd_id})
        self.account_usd = self.bank_journal_usd.default_debit_account_id

        self.transfer_account = self.env['res.users'].\
            browse(self.env.uid).company_id.transfer_account_id
        self.diff_income_account = self.env['res.users'].\
            browse(self.env.uid).company_id.\
            income_currency_exchange_account_id
        self.diff_expense_account = self.env['res.users'].\
            browse(self.env.uid).company_id.\
            expense_currency_exchange_account_id

    def create_invoice(self, amount=100,
                       type='out_invoice', currency_id=None,
                       partner=None, account_id=None):
        """ Returns an open invoice """
        invoice = self.invoice_model.create({
            'partner_id': partner or self.partner_agrolait.id,
            'currency_id': currency_id or self.currency_eur_id,
            'name': type,
            'account_id': account_id or self.account_receivable.id,
            'type': type,
            'date_invoice': time.strftime('%Y') + '-06-26',
        })
        self.invoice_line_model.create({
            'product_id': self.product.id,
            'quantity': 1,
            'price_unit': amount,
            'invoice_id': invoice.id,
            'name': 'something',
            'account_id': self.account_revenue.id,
        })
        invoice.action_invoice_open()
        return invoice

    def reconcile(self, liquidity_aml,
                  amount=0.0, amount_currency=0.0, currency_id=None):
        """ Reconcile a journal entry corresponding \
            to a payment with its bank statement line """
        bank_stmt = self.acc_bank_stmt_model.create({
            'journal_id': liquidity_aml.journal_id.id,
            'date': time.strftime('%Y') + '-07-15',
        })
        bank_stmt_line = self.acc_bank_stmt_line_model.create({
            'name': 'payment',
            'statement_id': bank_stmt.id,
            'partner_id': self.partner_agrolait.id,
            'amount': amount,
            'amount_currency': amount_currency,
            'currency_id': currency_id,
            'date': time.strftime('%Y') + '-07-15'
        })

        bank_stmt_line.process_reconciliation(payment_aml_rec=liquidity_aml)
        return bank_stmt

    def test_full_payment_process(self):
        """ Create a payment for two invoices, \
            post it and reconcile it with a bank statement """
        inv_1 = self.create_invoice(amount=100,
                                    currency_id=self.currency_eur_id,
                                    partner=self.partner_agrolait.id)
        inv_2 = self.create_invoice(amount=200,
                                    currency_id=self.currency_eur_id,
                                    partner=self.partner_agrolait.id)

        ctx = {'active_model': 'account.invoice',
               'active_ids': [inv_1.id, inv_2.id]}
        register_payments = self.register_payments_model.\
            with_context(ctx).\
            create({
                   'payment_date': time.strftime('%Y') + '-07-15',
                   'journal_id': self.bank_journal_euro.id,
                   'payment_method_id': self.payment_method_manual_in.id,
                   'group_invoices': True,
                   })
        register_payments.create_payments()
        payment = self.payment_model.search([], order="id desc", limit=1)

        self.assertAlmostEquals(payment.amount, 300)
        self.assertEqual(payment.state, 'posted')
        self.assertEqual(payment.state, 'posted')
        self.assertEqual(inv_1.state, 'paid')
        self.assertEqual(inv_2.state, 'paid')

        self.assertRecordValues(payment.move_line_ids, [
            {'account_id': self.account_eur.id,
             'debit': 300.0,
             'credit': 0.0,
             'amount_currency': 0,
             'currency_id': False},
            {'account_id': inv_1.account_id.id,
             'debit': 0.0,
             'credit': 300.0,
             'amount_currency': 0,
             'currency_id': False},
        ])
        self.assertTrue(payment.move_line_ids.
                        filtered(lambda l: l.account_id == inv_1.account_id)
                        [0].full_reconcile_id)

        liquidity_aml = payment.move_line_ids.\
            filtered(lambda r: r.account_id == self.account_eur)
        bank_statement = self.reconcile(liquidity_aml, 200, 0, False)

        self.assertEqual(liquidity_aml.statement_id, bank_statement)
        self.assertEqual(liquidity_aml.statement_line_id,
                         bank_statement.line_ids[0])

        self.assertEqual(payment.state, 'reconciled')
        self.assertEqual(payment.reconciliation_date,
                         inv_1.reconciliation_date)
