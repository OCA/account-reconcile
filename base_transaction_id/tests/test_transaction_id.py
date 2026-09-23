# Copyright 2022 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.sale.tests.common import TestSaleCommon


@tagged("post_install", "-at_install")
class TestTransactionID(TestSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order = (
            cls.env["sale.order"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "partner_id": cls.partner_a.id,
                    "order_line": [
                        Command.create(
                            {
                                "product_id": cls.company_data[
                                    "product_service_order"
                                ].id,
                                "product_uom_qty": 5,
                            }
                        )
                    ],
                }
            )
        )

    def test_transaction_propagation(self):
        """
        Check that transaction_id is propagated from sale order to the invoice.
        """
        # pre-condition: the sale order has the transaction set
        transaction_id = "Test transaction ID"
        self.sale_order.transaction_id = transaction_id

        # Confirm the SO
        self.sale_order.action_confirm()

        # Create regular invoice
        payment = (
            self.env["sale.advance.payment.inv"]
            .with_context(
                active_model=self.sale_order._name,
                active_ids=self.sale_order.ids,
                active_id=self.sale_order.id,
            )
            .create(
                {
                    "advance_payment_method": "delivered",
                }
            )
        )
        payment.create_invoices()

        # post-condition: there is an invoice
        # and has the same transaction of the sale order
        invoice = self.sale_order.invoice_ids[:1]
        self.assertTrue(invoice)
        self.assertEqual(invoice.transaction_id, transaction_id)
