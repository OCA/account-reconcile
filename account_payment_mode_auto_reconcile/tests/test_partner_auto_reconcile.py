# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from datetime import date, timedelta

from odoo.tests import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class TestPartnerAutoReconcile(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestPartnerAutoReconcile, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.acc_rec = cls.env["account.account"].create(
            {
                "name": "Receivable",
                "code": "RECEIVE",
                "account_type": "asset_receivable",
                "company_id": cls.env.ref("base.main_company").id,
            }
        )
        cls.acc_pay = cls.env["account.account"].create(
            {
                "name": "Payable",
                "code": "PAYABLE",
                "account_type": "liability_payable",
                "company_id": cls.env.ref("base.main_company").id,
            }
        )
        cls.acc_rev = cls.env["account.account"].create(
            {
                "name": "Income",
                "code": "INCOME",
                "account_type": "income",
                "company_id": cls.env.ref("base.main_company").id,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
                "customer_rank": 1,
                "property_account_receivable_id": cls.acc_rec.id,
                "property_account_payable_id": cls.acc_pay.id,
            }
        )
        cls.payment_mode = cls.env.ref("account_payment_mode.payment_mode_inbound_dd1")
        # TODO check why it's not set from demo data
        cls.payment_mode.auto_reconcile_outstanding_credits = True
        cls.product = cls.env.ref("product.consu_delivery_02")
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "BANK",
                "code": "BANK-TEST",
                "company_id": cls.env.ref("base.main_company").id,
                "type": "bank",
            }
        )

        cls.sale_journal = cls.env["account.journal"].create(
            {
                "name": "SALE-TEST",
                "code": "SALE",
                "company_id": cls.env.ref("base.main_company").id,
                "type": "sale",
            }
        )
        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "move_type": "out_invoice",
                "invoice_payment_term_id": cls.env.ref(
                    "account.account_payment_term_immediate"
                ).id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "name": cls.product.name,
                            "price_unit": 1000.0,
                            "quantity": 1,
                            "account_id": cls.acc_rev.id,
                        },
                    )
                ],
            }
        )

        cls.invoice.action_post()
        cls.refund_wiz = (
            cls.env["account.move.reversal"]
            .with_context(active_ids=cls.invoice.ids)
            .create(
                {
                    "refund_method": "refund",
                    "move_ids": [cls.invoice.id],
                    "journal_id": cls.sale_journal.id,
                }
            )
        )
        refund_id = cls.refund_wiz.reverse_moves().get("res_id")
        cls.refund = cls.env["account.move"].browse(refund_id)
        cls.payment = cls.env["account.payment"].create(
            {
                "amount": 500.0,
                "partner_id": cls.partner.id,
            }
        )
        cls.payment.action_post()
        cls.invoice_copy = cls.invoice.copy()
        cls.invoice_copy.write(
            {
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "name": cls.product.name,
                            "price_unit": 500.0,
                            "quantity": 1,
                            "account_id": cls.acc_rev.id,
                        },
                    )
                ]
            }
        )

    def test_invoice_validate_auto_reconcile(self):
        auto_rec_invoice = self.invoice.copy(
            {
                "payment_mode_id": self.payment_mode.id,
            }
        )
        auto_rec_invoice.action_post()
        self.assertTrue(self.payment_mode.auto_reconcile_outstanding_credits)
        self.assertEqual(self.invoice_copy.amount_residual, 1725.0)
        self.assertEqual(auto_rec_invoice.amount_residual, 650.0)

    def test_invoice_change_auto_reconcile(self):
        self.assertEqual(self.invoice_copy.amount_residual, 1725.0)
        self.invoice_copy.write({"payment_mode_id": self.payment_mode.id})
        self.invoice_copy.action_post()
        # Reconcile 500 from payment
        self.assertEqual(self.invoice_copy.amount_residual, 1225.0)
        self.invoice_copy.button_draft()
        self.invoice_copy.write({"payment_mode_id": False})
        self.invoice_copy.action_post()
        self.assertEqual(self.invoice_copy.amount_residual, 1725.0)
        # Copy the refund so there's more outstanding credit than invoice total
        new_refund = self.refund.copy()
        new_refund.date = (date.today() + timedelta(days=1)).strftime(DATE_FORMAT)
        new_refund.invoice_line_ids.write({"price_unit": 1200})
        new_refund.action_post()
        # Set reconcile partial to False
        self.payment_mode.auto_reconcile_allow_partial = False
        self.assertFalse(self.payment_mode.auto_reconcile_allow_partial)
        self.invoice_copy.write({"payment_mode_id": self.payment_mode.id})
        # Only the older move is used as payment
        self.assertEqual(self.invoice_copy.amount_residual, 1225.0)
        self.invoice_copy.write({"payment_mode_id": False})
        self.assertEqual(self.invoice_copy.amount_residual, 1725.0)
        # Set allow partial will reconcile both moves
        self.payment_mode.auto_reconcile_allow_partial = True
        self.invoice_copy.write({"payment_mode_id": self.payment_mode.id})
        self.assertEqual(self.invoice_copy.state, "posted")
        self.assertEqual(self.invoice_copy.amount_residual, 0)

    def test_invoice_auto_unreconcile(self):
        # Copy the refund so there's more outstanding credit than invoice total
        new_refund = self.refund.copy()
        new_refund.date = (date.today() + timedelta(days=1)).strftime(DATE_FORMAT)
        new_refund.invoice_line_ids.write({"price_unit": 1200})
        new_refund.action_post()
        auto_rec_invoice = self.invoice.copy(
            {
                "payment_mode_id": self.payment_mode.id,
            }
        )
        auto_rec_invoice.invoice_line_ids.write({"price_unit": 800})
        auto_rec_invoice.action_post()
        self.assertEqual(auto_rec_invoice.state, "posted")
        self.assertEqual(auto_rec_invoice.amount_residual, 0)
        # As we had 1880 (500 for payment and 1200 + 15% of new_fund) of
        # outstanding credits and 920 was assigned, there's 960 left

        self.assertTrue(self.payment_mode.auto_reconcile_allow_partial)
        self.invoice_copy.write({"payment_mode_id": self.payment_mode.id})
        self.invoice_copy.action_post()
        self.assertEqual(self.invoice_copy.amount_residual, 765.0)
        # Unreconcile of an invoice doesn't change the reconciliation of the
        # other invoice
        self.invoice_copy.button_draft()
        self.invoice_copy.write({"payment_mode_id": False})
        self.assertEqual(self.invoice_copy.amount_residual, 1725.0)
        self.assertEqual(auto_rec_invoice.state, "posted")
        self.assertEqual(auto_rec_invoice.amount_residual, 0)

    def test_invoice_auto_unreconcile_only_auto_reconcile(self):
        refund = self.refund.copy()
        refund.invoice_line_ids.write({"price_unit": 100})
        refund.action_post()
        new_invoice = self.invoice_copy.copy()
        new_invoice.action_post()
        # Only reconcile 1000 refund manually
        new_invoice_credits = new_invoice.invoice_outstanding_credits_debits_widget.get(
            "content"
        )
        for cred in new_invoice_credits:
            if cred.get("amount") == 115.0:
                new_invoice.js_assign_outstanding_line(cred.get("id"))
        self.assertEqual(new_invoice.amount_residual, 1610.0)
        # Assign payment mode adds the outstanding credit of 500
        new_invoice.write({"payment_mode_id": self.payment_mode.id})
        self.assertEqual(round(new_invoice.amount_residual, 2), 1110.0)
        # Remove payment mode only removes automatically added credit
        new_invoice.write({"payment_mode_id": False})
        self.assertEqual(new_invoice.amount_residual, 1610.0)

        # use the same payment partially on different invoices.
        other_invoice = self.invoice.copy()
        other_invoice.invoice_line_ids.write(
            {
                "price_unit": 200,
            }
        )
        other_invoice.write(
            {
                "payment_mode_id": self.payment_mode.id,
            }
        )
        other_invoice.action_post()
        self.assertEqual(other_invoice.state, "posted")
        # since 230 (200 + 15% VAT) were assigned on other invoice adding
        # auto-rec payment mode on new_invoice will reconcile 270
        # and residual will be 1340.0
        new_invoice.write({"payment_mode_id": self.payment_mode.id})
        self.assertEqual(new_invoice.amount_residual, 1340.0)
        # Removing the payment mode should not remove the partial payment on
        # the other invoice
        new_invoice.write({"payment_mode_id": False})
        self.assertEqual(new_invoice.amount_residual, 1610.0)
        self.assertEqual(other_invoice.state, "posted")

    def test_invoice_auto_reconcile_same_journal(self):
        """Check reconciling credits on same journal."""
        self.payment_mode.auto_reconcile_same_journal = True
        auto_rec_invoice = self.invoice.copy(
            {
                "payment_mode_id": self.payment_mode.id,
            }
        )

        payment_method_line = self.env["account.payment.method.line"].search(
            [
                ("code", "=", "manual"),
                ("payment_type", "=", "inbound"),
                ("journal_id", "=", self.journal.id),
            ]
        )
        self.invoice.journal_id.inbound_payment_method_line_ids = [
            payment_method_line.id
        ]

        payment_same_journal = self.env["account.payment"].create(
            {
                "amount": 500.0,
                "partner_id": self.partner.id,
                "journal_id": auto_rec_invoice.journal_id.id,
            }
        )
        payment_same_journal.action_post()

        self.assertTrue(self.payment_mode.auto_reconcile_outstanding_credits)
        self.assertEqual(self.invoice_copy.amount_residual, 1725.0)
        auto_rec_invoice.action_post()
        self.assertEqual(auto_rec_invoice.amount_residual, 650)

    def test_invoice_auto_reconcile_different_journal(self):
        """Check not reconciling credits on different journal."""
        self.payment_mode.auto_reconcile_same_journal = True
        auto_rec_invoice = self.invoice.copy(
            {
                "payment_mode_id": self.payment_mode.id,
                "journal_id": self.sale_journal.id,
            }
        )
        payment_different_journal = self.env["account.payment"].create(
            {
                "amount": 500.0,
                "partner_id": self.partner.id,
            }
        )
        payment_different_journal.action_post()
        auto_rec_invoice.action_post()
        self.assertTrue(self.payment_mode.auto_reconcile_outstanding_credits)
        self.assertEqual(self.invoice_copy.amount_residual, 1725.0)
        self.assertEqual(auto_rec_invoice.amount_residual, 1150.0)
