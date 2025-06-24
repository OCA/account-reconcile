from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPartialSettlement(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.payment_method = self.env.ref("account.account_payment_method_manual_in")
        self.payment = self.env["account.payment"].create(
            {
                "partner_id": self.partner.id,
                "amount": 500,
                "payment_type": "inbound",
                "payment_method_id": self.payment_method.id,
            }
        )
        self.payment.action_post()

        self.invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (0, 0, {"name": "Test Product", "quantity": 1, "price_unit": 500})
                ],
            }
        )
        self.invoice.action_post()

    def test_wizard_creation(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id, "payment_id": self.payment.id}
        )
        self.assertEqual(wizard.partner_id, self.partner)
        self.assertEqual(wizard.payment_id, self.payment)

    def test_compute_has_payments(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id}
        )
        wizard._compute_has_payments()
        self.assertTrue(wizard.has_payments)

        self.payment.unlink()
        wizard._compute_has_payments()
        self.assertFalse(wizard.has_payments)

    def test_compute_invoice_due(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id}
        )
        wizard._compute_invoice_due()
        self.assertEqual(wizard.total_invoice_due, self.invoice.amount_residual)

    def test_compute_payment_amount(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id, "payment_id": self.payment.id}
        )
        wizard._compute_payment_amount()
        self.assertEqual(wizard.payment_amount, 500)

    def test_compute_payment_residual_with_payment(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id, "payment_id": self.payment.id}
        )
        wizard._compute_payment_residual()
        self.assertTrue(wizard.payment_residual > 0)

    def test_compute_payment_residual_without_payment(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id}
        )
        wizard._compute_payment_residual()
        self.assertEqual(wizard.payment_residual, 0.0)

    def test_compute_total_to_reconcile(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id, "payment_id": self.payment.id}
        )
        self.env["partial.settlement.line"].create(
            {
                "wizard_id": wizard.id,
                "invoice_id": self.invoice.id,
                "partial_amount": 100,
            }
        )
        wizard._compute_total_to_reconcile()
        self.assertEqual(wizard.total_to_reconcile, 100)

    def test_onchange_partner_id(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id, "payment_id": self.payment.id}
        )
        wizard._onchange_partner_id()
        self.assertFalse(wizard.payment_id)
        self.assertFalse(wizard.line_ids)

    def test_onchange_payment_id(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id, "payment_id": self.payment.id}
        )
        wizard._onchange_payment_id()
        self.assertTrue(wizard.line_ids)

    def test_onchange_line_ids_payment_filter_customer(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id}
        )
        wizard._onchange_payment_id()
        for line in wizard.line_ids:
            line.invoice_id.move_type = "out_invoice"
        result = wizard._onchange_line_ids_payment_filter()
        self.assertIn("domain", result)

    def test_onchange_line_ids_payment_filter_vendor(self):
        vendor_invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "move_type": "in_invoice",
                "invoice_line_ids": [
                    (0, 0, {"name": "Vendor Product", "quantity": 1, "price_unit": 500})
                ],
            }
        )
        vendor_invoice = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                # "invoice_date": fields.Date.today(),  # ✅ Required for posting
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Vendor Product",
                            "quantity": 1,
                            "price_unit": 500,
                            "account_id": self.env["account.account"]
                            .search([("user_type_id.type", "=", "expense")], limit=1)
                            .id,
                        },
                    )
                ],
            }
        )
        vendor_invoice.action_post()

        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id}
        )
        wizard._onchange_payment_id()
        for line in wizard.line_ids:
            line.invoice_id.move_type = "in_invoice"
        result = wizard._onchange_line_ids_payment_filter()
        self.assertIn("domain", result)

    def test_reconcile_without_payment(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id}
        )
        with self.assertRaises(UserError):
            wizard.action_reconcile()

    def test_reconcile_without_amount(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id, "payment_id": self.payment.id}
        )
        with self.assertRaises(UserError):
            wizard.action_reconcile()

    def test_no_reconcilable_payment_lines(self):
        payment = self.env["account.payment"].create(
            {
                "partner_id": self.partner.id,
                "amount": 500,
                "payment_type": "inbound",
                "payment_method_id": self.payment_method.id,
            }
        )
        payment.action_post()

        for line in payment.move_id.line_ids:
            line.reconciled = True

        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id, "payment_id": payment.id}
        )
        with self.assertRaises(UserError):
            wizard.action_reconcile()

    def test_skipped_line_no_invoice_linked(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id, "payment_id": self.payment.id}
        )
        wizard._onchange_payment_id()
        for line in wizard.line_ids:
            line.partial_amount = 100
            line.invoice_id = False

        wizard._compute_total_to_reconcile()

        result = wizard.action_reconcile()
        self.assertEqual(result["type"], "ir.actions.client")

    def test_negative_reconciliation_direction(self):
        refund_invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "move_type": "out_refund",
                "invoice_line_ids": [
                    (0, 0, {"name": "Refund", "quantity": 1, "price_unit": 100})
                ],
            }
        )
        refund_invoice.action_post()

        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id, "payment_id": self.payment.id}
        )
        wizard._onchange_payment_id()

        for line in wizard.line_ids:
            line.partial_amount = line.amount_due
            line.invoice_id.move_type = "out_refund"

        wizard._compute_total_to_reconcile()

        result = wizard.action_reconcile()
        self.assertEqual(result["type"], "ir.actions.client")

    def test_forced_exception_in_reconcile(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id, "payment_id": self.payment.id}
        )
        wizard._onchange_payment_id()

        for line in wizard.line_ids:
            line.partial_amount = line.amount_due
            line.invoice_id = False

        wizard._compute_total_to_reconcile()

        with self.assertRaises(UserError):
            wizard.action_reconcile()
