# Copyright 2022 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, SavepointCase


class TestAccountMoveReconcileForbidCancel(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        purchase_journal = cls.env["account.journal"].create(
            {"name": "Purchase journal", "code": "PJ", "type": "purchase"}
        )
        sale_journal = cls.env["account.journal"].create(
            {"name": "Sale journal", "code": "SJ", "type": "sale"}
        )
        cls.env["account.journal"].create(
            {"name": "Bank Journal", "code": "BANK", "type": "bank"}
        )
        receivable_account_type = cls.env["account.account.type"].create(
            {
                "name": "Receivable account type",
                "type": "receivable",
                "internal_group": "asset",
            }
        )
        payable_account_type = cls.env["account.account.type"].create(
            {
                "name": "Payable account type",
                "type": "payable",
                "internal_group": "liability",
            }
        )
        income_account_type = cls.env["account.account.type"].create(
            {
                "name": "Income account type",
                "type": "other",
                "internal_group": "income",
            }
        )
        expense_account_type = cls.env["account.account.type"].create(
            {
                "name": "Expense account type",
                "type": "other",
                "internal_group": "expense",
            }
        )
        receivable_account = cls.env["account.account"].create(
            {
                "name": "Receivable Account",
                "code": "REC",
                "user_type_id": receivable_account_type.id,
                "reconcile": True,
            }
        )
        payable_account = cls.env["account.account"].create(
            {
                "name": "Payable Account",
                "code": "PAY",
                "user_type_id": payable_account_type.id,
                "reconcile": True,
            }
        )
        income_account = cls.env["account.account"].create(
            {
                "name": "Income Account",
                "code": "INC",
                "user_type_id": income_account_type.id,
                "reconcile": False,
            }
        )
        expense_account = cls.env["account.account"].create(
            {
                "name": "Expense Account",
                "code": "EXP",
                "user_type_id": expense_account_type.id,
                "reconcile": False,
            }
        )
        partner = cls.env["res.partner"].create(
            {
                "name": "Partner test",
                "property_account_receivable_id": receivable_account.id,
                "property_account_payable_id": payable_account.id,
            }
        )
        product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "property_account_income_id": income_account.id,
                "property_account_expense_id": expense_account.id,
            }
        )
        # Create a purchase invoice
        move_form = Form(
            cls.env["account.move"].with_context(default_type="in_invoice")
        )
        move_form.journal_id = purchase_journal
        move_form.partner_id = partner
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = product
            line_form.price_unit = 100.0
        cls.purchase_invoice = move_form.save()
        cls.purchase_invoice.action_post()
        # Create payment from invoice
        payment_register_form = Form(
            cls.env["account.payment"].with_context(
                active_model="account.move", active_ids=cls.purchase_invoice.ids,
            )
        )
        payment = payment_register_form.save()
        payment.post()
        # Create a sale invoice
        move_form = Form(
            cls.env["account.move"].with_context(default_type="out_invoice")
        )
        move_form.journal_id = sale_journal
        move_form.partner_id = partner
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = product
            line_form.price_unit = 100.0
        cls.sale_invoice = move_form.save()
        cls.sale_invoice.action_post()
        # Create payment from invoice
        payment_register_form = Form(
            cls.env["account.payment"].with_context(
                active_model="account.move", active_ids=cls.sale_invoice.ids,
            )
        )
        payment = payment_register_form.save()
        payment.post()

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
