import odoo.tests

from odoo.addons.account.tests.common import TestAccountReconciliationCommon


@odoo.tests.tagged("post_install", "-at_install")
class TestInvoice(TestAccountReconciliationCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_id = cls.env["res.partner"].create({"name": "test"})

    def test_multiple_transaction_ref(self):
        move = self.env["account.move"].create(
            {
                "transaction_id": "12345",
            }
        )
        move2 = self.env["account.move"].create({"name": "ABC"})
        self.assertEqual(move2._get_invoice_computed_reference(), "ABC")
        self.assertEqual(move._get_invoice_computed_reference(), "12345")
        order = self.env["sale.order"].create(
            {"partner_id": self.partner_id.id, "transaction_id": "54321"}
        )
        inv = order._prepare_invoice()
        self.assertEqual(inv.get("transaction_id"), "54321")
