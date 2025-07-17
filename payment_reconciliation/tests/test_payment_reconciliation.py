from datetime import date

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPartialSettlement(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})

        self.payment = self.env["account.payment"].create(
            {
                "partner_id": self.partner.id,
                "amount": 500.0,
                "payment_type": "inbound",
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
            }
        )
        self.payment.action_post()

        self.invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "move_type": "out_invoice",
                "invoice_date": date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Line",
                            "quantity": 1,
                            "price_unit": 500,
                            "account_id": self.env["account.account"]
                            .search(
                                [("account_type", "=", "asset_receivable")],
                                limit=1,
                            )
                            .id,
                        },
                    )
                ],
            }
        )
        self.invoice.action_post()

    def test_wizard_creation(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {
                "partner_id": self.partner.id,
                "payment_id": self.payment.id,
            }
        )
        self.assertEqual(wizard.partner_id, self.partner)
        self.assertEqual(wizard.payment_id, self.payment)

    def test_compute_methods(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {
                "partner_id": self.partner.id,
                "payment_id": self.payment.id,
            }
        )
        wizard._compute_payment_amount()
        wizard._compute_invoice_due()
        wizard._compute_payment_residual()
        wizard._compute_total_to_reconcile()
        self.assertGreaterEqual(wizard.payment_amount, 0)

    def test_onchange_partner_id(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id}
        )
        wizard._onchange_partner_id()
        self.assertEqual(wizard.payment_id, False)

    def test_onchange_payment_id(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {
                "partner_id": self.partner.id,
                "payment_id": self.payment.id,
            }
        )
        wizard._onchange_payment_id()
        self.assertTrue(wizard.line_ids)

    def test_reconcile_without_payment(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id}
        )
        with self.assertRaises(UserError):
            wizard.action_reconcile()

    def test_reconcile_without_amount(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {
                "partner_id": self.partner.id,
                "payment_id": self.payment.id,
            }
        )
        wizard._onchange_payment_id()
        for line in wizard.line_ids:
            line.partial_amount = 0
        with self.assertRaises(UserError):
            wizard.action_reconcile()

    def test_reconcile_success(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {
                "partner_id": self.partner.id,
                "payment_id": self.payment.id,
            }
        )
        wizard._onchange_payment_id()
        for line in wizard.line_ids:
            if line.invoice_id.id == self.invoice.id:
                line.partial_amount = 100.0
        res = wizard.action_reconcile()
        self.assertEqual(res.get("type"), "ir.actions.client")

    def test_partial_amount_exceeds_residual(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {
                "partner_id": self.partner.id,
                "payment_id": self.payment.id,
            }
        )
        wizard._onchange_payment_id()
        for line in wizard.line_ids:
            line.partial_amount = 1000.0
        with self.assertRaises(UserError):
            wizard.action_reconcile()

    def test_invoice_match_logic(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {
                "partner_id": self.partner.id,
                "payment_id": self.payment.id,
            }
        )
        wizard.line_ids = [
            (
                0,
                0,
                {
                    "invoice_date": self.invoice.invoice_date,
                    "amount_total": self.invoice.amount_total,
                    "amount_due": self.invoice.amount_residual,
                    "partial_amount": 50,
                },
            )
        ]
        res = wizard.action_reconcile()
        self.assertEqual(res["type"], "ir.actions.client")
