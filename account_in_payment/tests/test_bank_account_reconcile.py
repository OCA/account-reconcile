import time

from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import TestAccountReconciliationCommon


@tagged("post_install", "-at_install")
class TestReconciliationWidget(TestAccountReconciliationCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_get_invoice_in_payment_state=True,
            )
        )
        cls.acc_bank_stmt_model = cls.env["account.bank.statement"]
        cls.acc_bank_stmt_line_model = cls.env["account.bank.statement.line"]
        cls.bank_journal_usd.suspense_account_id = (
            cls.company.account_journal_suspense_account_id
        )
        cls.bank_journal_euro.suspense_account_id = (
            cls.company.account_journal_suspense_account_id
        )
        cls.current_assets_account = cls.env["account.account"].search(
            [
                ("internal_type", "=", "other"),
                ("internal_group", "=", "asset"),
                ("company_id", "=", cls.company.id),
            ],
            limit=1,
        )
        cls.current_assets_account.reconcile = True

    def test_payment(self):
        inv1 = self.create_invoice(
            currency_id=self.currency_euro_id,
            invoice_amount=100,
            move_type="in_invoice",
        )
        bank_stmt = self.acc_bank_stmt_model.create(
            {
                "company_id": self.env.ref("base.main_company").id,
                "journal_id": self.bank_journal_euro.id,
                "date": time.strftime("%Y-07-15"),
                "name": "test",
            }
        )
        bank_stmt_line = self.acc_bank_stmt_line_model.create(
            {
                "name": "testLine",
                "journal_id": self.bank_journal_euro.id,
                "statement_id": bank_stmt.id,
                "amount": -100,
                "date": time.strftime("%Y-07-15"),
                "payment_ref": "Test Payment Ref",
            }
        )
        payable1 = inv1.line_ids.filtered(
            lambda line: line.account_id.internal_type == "payable"
        )
        self.assertEqual(inv1.amount_residual_signed, -100)
        bank_stmt_line.process_reconciliation(
            [
                {
                    "move_line": payable1,
                    "debit": abs(bank_stmt_line.amount),
                    "credit": 0.0,
                    "currency_id": bank_stmt_line.currency_id.id,
                }
            ]
        )
        self.assertEqual(inv1.payment_state, "paid")

    def test_in_payment(self):
        inv1 = self.create_invoice(
            currency_id=self.currency_euro_id,
            invoice_amount=100,
            move_type="in_invoice",
        )
        action = inv1.action_register_payment()
        form = Form(
            self.env[action["res_model"]].with_context(
                mail_create_nolog=True, **action["context"]
            )
        )
        payments = form.save().action_create_payments()
        self.assertEqual(inv1.payment_state, "in_payment")
        bank_stmt = self.acc_bank_stmt_model.create(
            {
                "company_id": self.env.ref("base.main_company").id,
                "journal_id": self.bank_journal_euro.id,
                "date": time.strftime("%Y-07-15"),
                "name": "test",
            }
        )
        bank_stmt_line = self.acc_bank_stmt_line_model.create(
            {
                "name": "testLine",
                "journal_id": self.bank_journal_euro.id,
                "statement_id": bank_stmt.id,
                "amount": -100,
                "date": time.strftime("%Y-07-15"),
                "payment_ref": "Test Payment Ref",
            }
        )
        payment_records = self.env["account.payment"].browse(payments["res_id"])
        receivable1 = payment_records.line_ids.filtered(
            lambda line: not line.reconciled
        )
        self.assertEqual(inv1.amount_residual_signed, 0)
        self.assertFalse(receivable1.reconciled)
        bank_stmt_line.process_reconciliation(
            [
                {
                    "move_line": receivable1,
                    "debit": abs(bank_stmt_line.amount),
                    "credit": 0.0,
                    "currency_id": bank_stmt_line.currency_id.id,
                }
            ]
        )
        self.assertEqual(inv1.payment_state, "paid")
        self.assertEqual(inv1.amount_residual_signed, 0)
        self.assertTrue(receivable1.reconciled)
