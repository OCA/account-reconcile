# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.tests import tagged

from odoo.addons.account_reconcile_model_oca.tests.common import (
    TestAccountReconciliationCommon,
)


@tagged("post_install", "-at_install")
class TestAccountReconcileSaleOrder(TestAccountReconciliationCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env.ref("base.res_partner_12")  # Azure Interior
        cls.model = cls.env.ref(
            "account_reconcile_sale_order.reconcile_model_sale_order"
        )
        cls.model.sudo().company_id = cls.company
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Order line",
                            "price_unit": 4242,
                            "product_id": cls.env.ref("product.consu_delivery_01").id,
                        },
                    )
                ],
            }
        )
        cls.bank_statement = cls.env["account.bank.statement"].create(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "bank payment",
                            "amount": 4242,
                            "payment_ref": "/",
                            "partner_id": partner.id,
                        },
                    )
                ],
                "journal_id": cls.bank_journal_euro.id,
            }
        )

    def test_reconcile_sale_order(self):
        """Test that we find a sales order via reconciliation rules"""
        self.bank_statement.line_ids.payment_ref = self.sale_order.name
        self.assertEqual(self.sale_order.invoice_status, "no")
        rule_result = self.model._apply_rules(
            self.bank_statement.line_ids, self.bank_statement.line_ids.partner_id
        )
        self.assertTrue(rule_result, "No order found")
        self.assertEqual(rule_result["status"], "sale_order_matching")
        self.bank_statement.line_ids.clean_reconcile()
        self.bank_statement.line_ids.reconcile_bank_line()
        self.assertEqual(self.sale_order.invoice_status, "invoiced")

    def test_token_matching(self):
        """Test that we find orders by substrings of statement label"""
        self.model.sudo().sale_order_matching_token_match = True
        self.bank_statement.line_ids.payment_ref = f"payment for {self.sale_order.name}"
        rule_result = self.model._apply_rules(
            self.bank_statement.line_ids, self.bank_statement.line_ids.partner_id
        )
        self.assertTrue(rule_result, "No order found")
        self.assertEqual(rule_result["status"], "sale_order_matching")

    def test_manual_match(self):
        """Test that manual selection of sales order works"""
        statement_line = self.bank_statement.line_ids
        statement_line.clean_reconcile()
        self.assertFalse(
            any(
                "sale_order_id" in line
                for line in statement_line.reconcile_data_info["data"]
            )
        )
        statement_line.add_sale_order_id = self.sale_order
        statement_line._onchange_add_sale_order_id()
        self.assertTrue(
            any(
                "sale_order_id" in line
                for line in statement_line.reconcile_data_info["data"]
            )
        )
        statement_line.reconcile_bank_line()
        self.assertEqual(self.sale_order.invoice_status, "invoiced")
