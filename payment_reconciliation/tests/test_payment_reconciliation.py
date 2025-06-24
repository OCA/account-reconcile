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

    def test_wizard_creation(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {
                "partner_id": self.partner.id,
                "payment_id": self.payment.id,
            }
        )
        self.assertEqual(wizard.partner_id, self.partner)
        self.assertEqual(wizard.payment_id, self.payment)

    def test_compute_has_payments(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {"partner_id": self.partner.id}
        )
        # Case: Payment exists
        wizard._compute_has_payments()
        self.assertTrue(wizard.has_payments)

        # Case: No payment exists
        self.payment.unlink()
        wizard._compute_has_payments()
        self.assertFalse(wizard.has_payments)

    def test_reconcile_without_amount(self):
        wizard = self.env["partial.settlement.wizard"].create(
            {
                "partner_id": self.partner.id,
                "payment_id": self.payment.id,
            }
        )
        with self.assertRaises(UserError):
            wizard.action_reconcile()
