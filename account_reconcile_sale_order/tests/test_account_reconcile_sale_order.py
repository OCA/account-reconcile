# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.tests import tagged
from odoo.tools.misc import mute_logger

from odoo.addons.account.tests.common import TestAccountReconciliationCommon


@tagged("post_install", "-at_install")
class TestAccountReconcileSaleOrder(TestAccountReconciliationCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        partner = cls.env.ref("base.res_partner_12")  # Azure Interior
        cls.model = cls.env.ref(
            "account_reconcile_sale_order.reconcile_model_sale_order"
        )
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
        """Test that we find a sale order via reconciliation rules"""
        self.bank_statement.line_ids.payment_ref = self.sale_order.name
        self.assertEqual(self.sale_order.invoice_status, "no")
        rule_result = self.model.sudo()._apply_rules(self.bank_statement.line_ids)
        line_result = rule_result[self.bank_statement.line_ids.id]
        self.assertTrue(line_result, "No order found")
        self.assertEqual(line_result["status"], "sale_order_matching")
        self.bank_statement.line_ids.process_reconciliation(
            new_aml_dicts=line_result["write_off_vals"],
        )
        self.assertEqual(self.sale_order.invoice_status, "invoiced")

    def test_token_matching(self):
        """Test that we find orders by substrings of statement label"""
        self.model.sudo().sale_order_matching_token_match = True
        self.bank_statement.line_ids.payment_ref = (
            "payment for %s" % self.sale_order.name
        )
        rule_result = self.model.sudo()._apply_rules(self.bank_statement.line_ids)
        line_result = rule_result[self.bank_statement.line_ids.id]
        self.assertTrue(line_result, "No order found")
        self.assertEqual(line_result["status"], "sale_order_matching")

    @mute_logger(
        "odoo.addons.account_reconciliation_widget.models.reconciliation_widget"
    )
    # the base module logs a warning if search_str is not a number
    def test_manual_match(self):
        """Test that we find orders when users fill in a name of a partner"""
        widget = self.env["account.reconciliation.widget"]
        propositions = widget.get_move_lines_for_bank_statement_line(
            self.bank_statement.line_ids.id,
            search_str=self.sale_order.partner_id.email,
            mode="rp",
        )
        self.assertTrue(propositions, "Sale order not found")
        self.assertEqual(
            propositions[0].get("sale_order_id"),
            self.sale_order.id,
            "Sale order not found",
        )
