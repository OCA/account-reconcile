# Copyright 2022 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestAccountMoveReconcileForbidCancel(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.env["account.journal"].create(
            {"name": "Bank Journal", "code": "BANK", "type": "bank"}
        )
        receivable_account = cls.env["account.account"].create(
            {
                "name": "Receivable Account",
                "code": "REC",
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        payable_account = cls.env["account.account"].create(
            {
                "name": "Payable Account",
                "code": "PAY",
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )
        income_account = cls.env["account.account"].create(
            {
                "name": "Income Account",
                "code": "INC",
                "user_type_id": cls.env.ref(
                    "account.data_account_type_other_income"
                ).id,
                "reconcile": False,
            }
        )
        expense_account = cls.env["account.account"].create(
            {
                "name": "Expense Account",
                "code": "EXP",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
                "reconcile": False,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner test",
                "property_account_receivable_id": receivable_account.id,
                "property_account_payable_id": payable_account.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "property_account_income_id": income_account.id,
                "property_account_expense_id": expense_account.id,
            }
        )
        # Create a purchase invoice
        cls.purchase_invoice = cls._create_invoice(cls, "in_invoice")
        cls.purchase_invoice.action_post()
        # Create payment from invoice
        cls._create_payment_from_invoice(cls, cls.purchase_invoice)
        # Create a sale invoice
        cls.sale_invoice = cls._create_invoice(cls, "out_invoice")
        cls.sale_invoice.action_post()
        # Create payment from invoice
        cls._create_payment_from_invoice(cls, cls.sale_invoice)

    def _create_invoice(self, move_type):
        move_form = Form(
            self.env["account.move"].with_context(default_move_type=move_type)
        )
        move_form.invoice_date = fields.Date.today()
        move_form.partner_id = self.partner
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product
            line_form.price_unit = 100.0
        return move_form.save()

    def _create_payment_from_invoice(self, invoice):
        res = invoice.action_register_payment()
        payment_register_form = Form(
            self.env[res["res_model"]].with_context(**res["context"])
        )
        payment = payment_register_form.save()
        payment.action_create_payments()

    def test_reset_invoice_to_draft(self):
        with self.assertRaises(ValidationError):
            self.purchase_invoice.with_context(
                test_reconcile_forbid_cancel=True
            ).button_draft()
        with self.assertRaises(ValidationError):
            self.sale_invoice.with_context(
                test_reconcile_forbid_cancel=True
            ).button_draft()

    def test_cancel_invoice(self):
        with self.assertRaises(ValidationError):
            self.purchase_invoice.with_context(
                test_reconcile_forbid_cancel=True
            ).button_cancel()
        with self.assertRaises(ValidationError):
            self.sale_invoice.with_context(
                test_reconcile_forbid_cancel=True
            ).button_cancel()

    def test_extra_invoice_process_to_draft(self):
        invoice = self._create_invoice("out_invoice")
        invoice.action_post()
        invoice.button_draft()
        self.assertEqual(invoice.state, "draft")

    def test_extra_invoice_process_cancel(self):
        invoice = self._create_invoice("out_invoice")
        invoice.action_post()
        invoice.button_cancel()
        self.assertEqual(invoice.state, "cancel")
