# Copyright (C) 2021, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestAccountReconcileReconciliationDate(AccountTestInvoicingCommon):
    def setUp(self):
        super(TestAccountReconcileReconciliationDate, self).setUp()
        self.register_payments_model = self.env[
            "account.payment.register"
        ].with_context(active_model="account.move")
        self.payment_model = self.env["account.payment"]
        self.invoice_model = self.env["account.move"]
        self.invoice_line_model = self.env["account.move.line"]
        self.acc_bank_stmt_model = self.env["account.bank.statement"]
        self.acc_bank_stmt_line_model = self.env["account.bank.statement.line"]

        self.partner_agrolait = self.env.ref("base.res_partner_2")
        self.partner_china_exp = self.env.ref("base.res_partner_3")
        self.currency_chf_id = self.env.ref("base.CHF").id
        self.currency_usd_id = self.env.ref("base.USD").id
        self.currency_eur_id = self.env.ref("base.EUR").id

        company = self.env.ref("base.main_company")
        self.cr.execute(
            "UPDATE res_company SET currency_id = %s WHERE id = %s",
            [self.currency_eur_id, company.id],
        )
        self.product = self.env.ref("product.product_product_4")
        self.payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in"
        )
        self.payment_method_manual_out = self.env.ref(
            "account.account_payment_method_manual_out"
        )

        self.account_receivable = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_receivable").id,
                )
            ],
            limit=1,
        )
        self.account_payable = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_payable").id,
                )
            ],
            limit=1,
        )
        self.account_revenue = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_revenue").id,
                )
            ],
            limit=1,
        )

        self.bank_journal_euro = self.env["account.journal"].search(
            [("type", "=", "bank")], limit=1
        )
        self.account_eur = self.bank_journal_euro.default_account_id

        self.bank_journal_usd = self.env["account.journal"].create(
            {
                "name": "Bank US",
                "type": "bank",
                "code": "BNK68",
                "currency_id": self.currency_usd_id,
            }
        )
        self.account_usd = self.bank_journal_usd.default_account_id
        self.journal_id = self.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        self.transfer_account = (
            self.env["res.users"].browse(self.env.uid).company_id.transfer_account_id
        )
        self.diff_income_account = (
            self.env["res.users"]
            .browse(self.env.uid)
            .company_id.income_currency_exchange_account_id
        )
        self.diff_expense_account = (
            self.env["res.users"]
            .browse(self.env.uid)
            .company_id.expense_currency_exchange_account_id
        )

    def create_invoice(
        self,
        amount=100,
        move_type="out_invoice",
        currency_id=None,
        partner=None,
        account_id=None,
    ):
        """ Returns an open invoice """
        invoice = self.invoice_model.create(
            {
                "partner_id": partner or self.partner_agrolait.id,
                "currency_id": currency_id or self.currency_eur_id,
                "journal_id": self.journal_id.id,
                "move_type": move_type,
                "invoice_date": time.strftime("%Y") + "-06-26",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": amount,
                            "name": "something",
                            "account_id": self.journal_id.default_account_id.id,
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        return invoice

    def reconcile(
        self, liquidity_aml, amount=0.0, amount_currency=0.0, currency_id=None
    ):
        """ Reconcile a journal entry corresponding \
            to a payment with its bank statement line """
        bank_stmt = self.acc_bank_stmt_model.create(
            {
                "journal_id": liquidity_aml.journal_id.id,
                "date": time.strftime("%Y") + "-07-15",
            }
        )
        bank_stmt_line = self.acc_bank_stmt_line_model.create(
            {
                "name": "payment",
                "statement_id": bank_stmt.id,
                "partner_id": self.partner_agrolait.id,
                "amount": amount,
                "amount_currency": amount_currency,
                "currency_id": currency_id,
                "date": time.strftime("%Y") + "-07-15",
            }
        )

        bank_stmt_line.process_reconciliation(payment_aml_rec=liquidity_aml)
        return bank_stmt

    def test_full_payment_process(self):
        """ Create a payment for two invoices, \
            post it and reconcile it with a bank statement """
        inv_1 = self.create_invoice(
            amount=100,
            currency_id=self.currency_eur_id,
            partner=self.partner_agrolait.id,
        )
        inv_2 = self.create_invoice(
            amount=200,
            currency_id=self.currency_eur_id,
            partner=self.partner_agrolait.id,
        )

        ctx = {"active_model": "account.move", "active_ids": [inv_1.id, inv_2.id]}
        register_payments = self.register_payments_model.with_context(ctx).create(
            {
                "payment_date": time.strftime("%Y") + "-07-15",
                "journal_id": self.bank_journal_euro.id,
                "payment_method_id": self.payment_method_manual_in.id,
            }
        )
        register_payments.flush()
        register_payments.action_create_payments()
        payment = self.payment_model.search([], order="id desc", limit=1)

        self.assertAlmostEqual(payment.amount, 200)
        self.assertEqual(payment.state, "posted")
        self.assertEqual(payment.state, "posted")
        self.assertEqual(inv_1.payment_state, "paid")
        self.assertEqual(inv_2.payment_state, "paid")

        self.assertRecordValues(
            payment.line_ids,
            [
                {
                    "journal_id": self.bank_journal_euro.id,
                    "debit": 200.0,
                    "credit": 0.0,
                },
                {
                    "journal_id": self.bank_journal_euro.id,
                    "debit": 0.0,
                    "credit": 200.0,
                },
            ],
        )

        self.assertEqual(payment.state, "posted")
        self.assertEqual(payment.reconciliation_date, inv_1.reconciliation_date)
