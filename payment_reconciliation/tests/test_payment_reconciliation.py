# payment_reconciliation/tests/test_payment_reconciliation.py
from datetime import date

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPartialSettlement(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.currency = self.env.company.currency_id

        self.invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "quantity": 1,
                            "price_unit": 500,
                            "account_id": self.env["account.account"]
                            .search(
                                [("account_type", "=", "asset_receivable")], limit=1
                            )
                            .id,
                        },
                    )
                ],
            }
        )
        self.invoice.action_post()

        self.payment = self.env["account.payment"].create(
            {
                "partner_id": self.partner.id,
                "amount": 500,
                "payment_type": "inbound",
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )
        self.payment.action_post()

    def create_wizard(self, partial_amount=0.0):
        wizard = self.env["partial.settlement.wizard"].create(
            {
                "partner_id": self.partner.id,
                "payment_id": self.payment.id,
            }
        )
        wizard._onchange_payment_id()

        if wizard.line_ids:
            wizard.line_ids[0].partial_amount = partial_amount
        return wizard

    def test_onchange_payment_id_populates_lines(self):
        wizard = self.create_wizard()
        self.assertTrue(wizard.line_ids)
        self.assertEqual(wizard.line_ids[0].amount_due, self.invoice.amount_residual)

    def test_compute_fields(self):
        wizard = self.create_wizard(100)
        wizard._compute_invoice_due()
        wizard._compute_total_to_reconcile()
        wizard._compute_payment_residual()
        self.assertGreater(wizard.total_invoice_due, 0)
        self.assertEqual(wizard.total_to_reconcile, 100)
        self.assertGreaterEqual(wizard.payment_residual, 0)

    def test_reconcile_success(self):
        wizard = self.create_wizard(500)
        action = wizard.action_reconcile()
        self.assertEqual(action["type"], "ir.actions.client")

    def test_reconcile_no_payment(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        with self.assertRaises(UserError):
            wizard.action_reconcile()

    def test_reconcile_zero_amount(self):
        wizard = self.create_wizard(0)
        with self.assertRaises(UserError):
            wizard.action_reconcile()

    def test_reconcile_exceeds_amount(self):
        wizard = self.create_wizard(600)
        with self.assertRaises(UserError):
            wizard.action_reconcile()

    def test_onchange_line_ids_payment_filter(self):
        wizard = self.create_wizard(100)
        result = wizard._onchange_line_ids_payment_filter()
        self.assertIn("domain", result)
        self.assertIn("payment_id", result["domain"])

    def test_onchange_partner_id(self):
        wizard = self.create_wizard()
        result = wizard._onchange_partner_id()
        self.assertIn("domain", result)
        self.assertFalse(wizard.payment_id)
        self.assertEqual(wizard.line_ids, self.env["partial.settlement.line"])
