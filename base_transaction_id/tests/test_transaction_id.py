# Copyright 2022 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.fields import first
from odoo.tests import Form

from odoo.addons.sale.tests.common import TestSaleCommon


class TestTransactionID(TestSaleCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        sale_order_form = Form(
            cls.env["sale.order"].with_context(
                tracking_disable=True,
            )
        )
        sale_order_form.partner_id = cls.partner_a
        with sale_order_form.order_line.new() as sale_line:
            sale_line.product_id = cls.company_data["product_service_order"]
            sale_line.product_uom_qty = 5
        cls.sale_order = sale_order_form.save()

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
        payment_form = Form(
            self.env["sale.advance.payment.inv"].with_context(
                active_model=self.sale_order._name,
                active_ids=self.sale_order.ids,
                active_id=self.sale_order.id,
            )
        )
        payment_form.advance_payment_method = "delivered"
        payment = payment_form.save()
        payment.create_invoices()

        # post-condition: there is an invoice
        # and has the same transaction of the sale order
        invoice = first(self.sale_order.invoice_ids)
        self.assertTrue(invoice)
        self.assertEqual(invoice.transaction_id, transaction_id)
