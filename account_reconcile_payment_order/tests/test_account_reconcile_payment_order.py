# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - João Marques
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests

from odoo.addons.account_payment_order.tests.test_payment_order_inbound import (
    TestPaymentOrderInboundBase,
)


@odoo.tests.tagged("post_install", "-at_install")
class TestAccountReconcilePaymentOrder(TestPaymentOrderInboundBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.widget_obj = cls.env["account.reconciliation.widget"]
        cls.bank_journal = cls.env["account.journal"].create(
            {"name": "Test bank journal", "type": "bank"}
        )
        # Create second invoice for being sure it handles the payment order
        cls.invoice2 = cls._create_customer_invoice(cls)
        cls.partner2 = cls.env["res.partner"].create({"name": "Test partner 2"})
        # Set correct partner in invoice
        cls.invoice2.partner_id = cls.partner2.id
        for line in cls.invoice2.line_ids:
            line.partner_id = cls.partner2.id
        cls.invoice2.payment_mode_id = cls.inbound_mode
        cls.invoice2.action_post()
        # Add to payment order using the wizard
        cls.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=cls.invoice2.ids
        ).create({}).run()
        # Prepare statement
        cls.statement = cls.env["account.bank.statement"].create(
            {
                "name": "Test statement",
                "date": "2019-01-01",
                "journal_id": cls.bank_journal.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "date": "2019-01-01",
                            "name": "Test line",
                            "amount": 200,  # 100 * 2
                            "payment_ref": "payment",
                        },
                    ),
                ],
            }
        )

    def test_reconcile_payment_order_bank(self):
        self.assertEqual(len(self.inbound_order.payment_line_ids), 2)
        # Prepare payment order
        self.inbound_order.draft2open()
        self.inbound_order.open2generated()
        self.inbound_order.generated2uploaded()
        # Check widget result
        res = self.widget_obj.get_bank_statement_line_data(self.statement.line_ids.ids)
        self.assertEqual(len(res["lines"][0]["reconciliation_proposition"]), 2)

    def test_reconcile_payment_order_transfer_account(self):
        self.assertEqual(len(self.inbound_order.payment_line_ids), 2)
        self.inbound_mode.write(
            {
                "default_journal_ids": [(4, self.bank_journal.id)],
            }
        )
        self.assertEqual(len(self.inbound_order.payment_line_ids), 2)
        # Prepare payment order
        self.inbound_order.draft2open()
        self.inbound_order.open2generated()
        self.inbound_order.generated2uploaded()
        # Check widget result
        res = self.widget_obj.get_bank_statement_line_data(self.statement.line_ids.ids)
        proposition = res["lines"][0]["reconciliation_proposition"]
        self.assertEqual(len(proposition), 2)
        # Reconcile that entries and check again
        st_line_vals = res["lines"][0]["st_line"]
        self.widget_obj.process_move_lines(
            data=[
                {
                    "type": "",
                    "mv_line_ids": [proposition[0]["id"], proposition[1]["id"]],
                    "new_mv_line_dicts": [
                        {
                            "name": st_line_vals["name"],
                            "credit": st_line_vals["amount"],
                            "debit": 0,
                            "account_id": st_line_vals["account_id"][0],
                            "journal_id": st_line_vals["journal_id"],
                        }
                    ],
                }
            ],
        )
        res2 = self.widget_obj.get_bank_statement_line_data(
            self.statement.line_ids.ids,
        )
        self.assertNotEqual(res, res2)
