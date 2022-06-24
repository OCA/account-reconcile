# Copyright 2022 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, SavepointCase


class TestAccountMoveReconcileForbidCancel(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        journal_sale = cls.env["account.journal"].create(
            {"name": "Sale journal", "code": "SJ", "type": "sale"}
        )
        receivable_account_type = cls.env["account.account.type"].create(
            {
                "name": "Receivable account type",
                "type": "receivable",
                "internal_group": "asset",
            }
        )
        income_account_type = cls.env["account.account.type"].create(
            {
                "name": "Income account type",
                "type": "other",
                "internal_group": "income",
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
        income_account = cls.env["account.account"].create(
            {
                "name": "Income Account",
                "code": "INC",
                "user_type_id": income_account_type.id,
                "reconcile": False,
            }
        )
        partner = cls.env["res.partner"].create(
            {
                "name": "Partner test",
                "property_account_receivable_id": receivable_account.id,
            }
        )
        product = cls.env["product.product"].create(
            {"name": "Product Test", "property_account_income_id": income_account.id}
        )
        # Create invoice
        move_form = Form(
            cls.env["account.move"].with_context(default_type="out_invoice")
        )
        move_form.journal_id = journal_sale
        move_form.partner_id = partner
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = product
            line_form.price_unit = 100.0
        cls.invoice = move_form.save()
        cls.invoice.action_post()
        # Create payment from invoice
        cls.env["account.journal"].create(
            {"name": "Bank Journal", "code": "BANK", "type": "bank"}
        )
        payment_register = Form(
            cls.env["account.payment"].with_context(
                active_model="account.move", active_ids=cls.invoice.ids,
            )
        )
        cls.payment = payment_register.save()
        cls.payment.post()

    def test_reset_invoice_to_draft(self):
        with self.assertRaises(ValidationError):
            self.invoice.button_draft()

    def test_cancel_invoice(self):
        with self.assertRaises(ValidationError):
            self.invoice.button_cancel()
