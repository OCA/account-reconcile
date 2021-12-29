# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime

from odoo.tests.common import tagged

from odoo.addons.account.tests.common import TestAccountReconciliationCommon


@tagged("post_install", "-at_install")
class TestCompletionTransactionId(TestAccountReconciliationCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.sale_journal = cls.company_data["default_journal_sale"]
        cls.sale_journal.used_for_completion = True
        cls.move = cls.env["account.move"].create(
            {
                "name": "Move with transaction ID",
                "ref": "credit card remittance",
                "journal_id": cls.sale_journal.id,
            }
        )
        cls.move_line = cls.env["account.move.line"].create(
            {
                "name": "XXX66Z",
                "account_id": cls.account_euro.id,
                "move_id": cls.move.id,
                "ref": "some reference",
                "date_maturity": "{}-01-06".format(datetime.now().year),
                "credit": 0.0,
            }
        )

    def test_sale_order_transaction_id(self):
        self.move_line.name = "XXX66Z"
        self.sale_journal.rule_ids = [
            (
                4,
                self.env.ref(
                    "account_move_transactionid_import."
                    "bank_statement_completion_rule_4"
                ).id,
                False,
            ),
            (
                4,
                self.env.ref(
                    "account_move_base_import.bank_statement_completion_rule_2"
                ).id,
                False,
            ),
            (
                4,
                self.env.ref(
                    "account_move_base_import.bank_statement_completion_rule_3"
                ).id,
                False,
            ),
            (
                4,
                self.env.ref(
                    "account_move_base_import.bank_statement_completion_rule_4"
                ).id,
                False,
            ),
            (
                4,
                self.env.ref(
                    "account_move_base_import.bank_statement_completion_rule_5"
                ).id,
                False,
            ),
        ]

        lines = self.move.line_ids.sorted("debit")

        self.move.with_context({"check_move_validity": False}).write(
            {
                "line_ids": [
                    (1, lines[0].id, {"credit": lines[0].credit + 118.4}),
                    (
                        0,
                        None,
                        {
                            "name": "line 1",
                            "account_id": self.company_data[
                                "default_account_revenue"
                            ].id,
                            "debit": 118.4,
                            "credit": 0.0,
                        },
                    ),
                ],
            }
        )
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "note": "Invoice after delivery",
                "transaction_id": "XXX66Z",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref("product.product_product_7").id,
                            "product_uom_qty": 8,
                        },
                    )
                ],
            }
        )
        self.assertEqual(so.transaction_id, "XXX66Z")
        self.move.button_auto_completion()
        self.assertEqual(self.move_line.partner_id.name, self.partner.name)

    def test_new_invoice_with_transaction_id(self):
        self.move_line.name = "XXX77Z"
        self.move_line.partner_id = None
        self.sale_journal.used_for_completion = True
        self.sale_journal.rule_ids = [
            (
                4,
                self.env.ref(
                    "account_move_transactionid_import."
                    "bank_statement_completion_rule_trans_id_invoice"
                ).id,
                False,
            )
        ]
        invoice = (
            self.env["account.move"]
            # ir.attachment.type changed from out_invoice to url
            .with_context(default_type="url").create(
                {
                    "currency_id": self.env.ref("base.EUR").id,
                    "move_type": "out_invoice",
                    "partner_id": self.partner.id,
                    "transaction_id": "XXX77Z",
                    "ref": "none",
                    "journal_id": self.sale_journal.id,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "[PCSC234] PC Assemble SC234",
                                "price_unit": 450.0,
                                "quantity": 1.0,
                                "product_id": self.env.ref(
                                    "product.product_product_3"
                                ).id,
                                "product_uom_id": self.env.ref(
                                    "uom.product_uom_unit"
                                ).id,
                                "account_id": self.account_euro.id,
                            },
                        )
                    ],
                }
            )
        )
        self.assertEqual(invoice.state, "draft")
        self.move.button_auto_completion()
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")
        self.assertEqual(self.move_line.partner_id, self.partner)
