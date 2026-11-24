# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import tagged

from .common import StripeImportCommon, balance_transaction


@tagged("post_install", "-at_install")
class TestStripeCompletion(StripeImportCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stripe_journal.write(
            {
                "used_for_completion": True,
                "launch_import_completion": True,
                "rule_ids": [
                    Command.set(
                        cls.env.ref(
                            "account_move_stripe_import.bank_statement_completion_rule_trans_ref_so"
                        ).ids
                    )
                ],
            }
        )
        cls.customer_receivable = cls.copy_account(
            cls.company_data["default_account_receivable"]
        )
        cls.customer = cls.env["res.partner"].create({"name": "Stripe customer"})
        cls.customer.with_company(
            cls.company_data["company"]
        ).property_account_receivable_id = cls.customer_receivable

    def _create_orders_transaction(self, reference, *partners, company=None):
        orders = self.env["sale.order"].create(
            [
                {
                    "company_id": (company or self.company_data["company"]).id,
                    "partner_id": partner.id,
                    "order_line": [Command.create({"product_id": self.product_a.id})],
                }
                for partner in partners
            ]
        )
        return self._create_transaction(
            "direct",
            reference=reference,
            partner_id=partners[0].id,
            sale_order_ids=[Command.set(orders.ids)],
        )

    def _import_stripe_transaction_line(self, description, amount, txn_type):
        self._add_stripe_payout(
            "po_1",
            1700100000,
            [
                balance_transaction(
                    "txn_1",
                    amount,
                    txn_type,
                    "ch_1",
                    1700000000,
                    description=description,
                ),
                balance_transaction("txn_po_1", -amount, "payout", "po_1", 1700100000),
            ],
        )
        self._run_stripe_import_cron()
        return self._stripe_entries().line_ids.filtered(
            lambda line: line.name == description
        )

    def test_payment_gets_partner_of_linked_order(self):
        self._create_orders_transaction("S00012", self.customer)

        line = self._import_stripe_transaction_line("S00012", 1000, "charge")

        self.assertEqual(line.partner_id, self.customer)
        self.assertEqual(line.account_id, self.customer_receivable)
        self.assertTrue(line.already_completed)

    def test_refund_gets_partner_of_refunded_payment_order(self):
        self._create_orders_transaction("S00012", self.customer)

        line = self._import_stripe_transaction_line(
            "REFUND FOR CHARGE (S00012)", -500, "refund"
        )

        self.assertEqual(line.partner_id, self.customer)
        self.assertEqual(line.account_id, self.customer_receivable)
        self.assertEqual(line.debit, 5.0)

    def test_reference_of_orders_of_several_partners_is_not_completed(self):
        other_customer = self.env["res.partner"].create({"name": "Other customer"})
        self._create_orders_transaction("S00012", self.customer, other_customer)

        line = self._import_stripe_transaction_line("S00012", 1000, "charge")

        self.assertFalse(line.partner_id)
        self.assertFalse(line.already_completed)
        self.assertIn(
            'Line named "S00012" was matched by more than one partner.',
            line.move_id.completion_logs,
        )

    def test_order_of_another_company_is_ignored(self):
        other_company = self.setup_other_company()["company"]
        self._create_orders_transaction("S00012", self.customer, company=other_company)

        line = self._import_stripe_transaction_line("S00012", 1000, "charge")

        self.assertFalse(line.partner_id)
        self.assertFalse(line.already_completed)

    def test_unknown_reference_is_left_without_partner(self):
        self._create_orders_transaction("S00012", self.customer)

        line = self._import_stripe_transaction_line("S00099", 1000, "charge")

        self.assertFalse(line.partner_id)
        self.assertEqual(
            line.account_id, self.company_data["default_account_receivable"]
        )
        self.assertFalse(line.already_completed)
