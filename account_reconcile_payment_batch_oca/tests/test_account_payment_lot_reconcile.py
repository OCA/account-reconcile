# Copyright 2024 Dixmit
# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, fields
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestReconciliationWidget(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env.user.write(
            {
                "groups_id": [
                    Command.link(
                        cls.env.ref(
                            "account_payment_batch_oca.group_account_payment"
                        ).id
                    )
                ]
            }
        )
        cls.company = cls.company_data["company"]
        cls.stmt_line_model = cls.env["account.bank.statement.line"]
        cls.bank_journal = cls.company_data["default_journal_bank"]
        # We need to make some fields visible in order to make the tests work
        cls.env["ir.ui.view"].create(
            {
                "name": "DEMO Account bank statement",
                "model": "account.bank.statement.line",
                "inherit_id": cls.env.ref(
                    "account_reconcile_oca.bank_statement_line_form_reconcile_view"
                ).id,
                "arch": """
            <data>
                <field name="manual_reference" position="attributes">
                    <attribute name="invisible">0</attribute>
                </field>
                <field name="manual_delete" position="attributes">
                    <attribute name="invisible">0</attribute>
                </field>
                <field name="partner_id" position="attributes">
                    <attribute name="invisible">0</attribute>
                </field>
            </data>
            """,
            }
        )
        cls.payment_method_in = (
            cls.env["account.payment.method"]
            .sudo()
            .create(
                {
                    "name": "test inbound reconcile",
                    "code": "test_manual",
                    "payment_type": "inbound",
                    "payment_order_ok": True,
                }
            )
        )
        cls.inbound_method = cls.env["account.payment.method.line"].create(
            {
                "name": "Test direct debit of customers",
                "company_id": cls.company.id,
                "journal_id": cls.bank_journal.id,
                "payment_method_id": cls.payment_method_in.id,
                "selectable": True,
            }
        )
        cls.inbound_order = cls.env["account.payment.order"].create(
            {
                "payment_type": "inbound",
                "payment_method_line_id": cls.inbound_method.id,
                "journal_id": cls.bank_journal.id,
                "company_id": cls.company.id,
            }
        )
        cls.payment_method_out = (
            cls.env["account.payment.method"]
            .sudo()
            .create(
                {
                    "name": "test outbound reconcile",
                    "code": "test_manual",
                    "payment_type": "outbound",
                    "payment_order_ok": True,
                }
            )
        )
        cls.outbound_method = cls.env["account.payment.method.line"].create(
            {
                "name": "Test Credit Transfer to Suppliers",
                "company_id": cls.company.id,
                "journal_id": cls.bank_journal.id,
                "payment_method_id": cls.payment_method_out.id,
                "selectable": True,
            }
        )
        cls.outbound_order = cls.env["account.payment.order"].create(
            {
                "payment_type": "outbound",
                "payment_method_line_id": cls.outbound_method.id,
                "journal_id": cls.bank_journal.id,
                "company_id": cls.company.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test partner1"})
        cls.partner2 = cls.env["res.partner"].create({"name": "Test partner2"})

    def create_invoice_order(self, order, partner):
        # Create invoice
        move_type = "in_invoice"
        account_type = "expense"
        if order.payment_type == "inbound":
            move_type = "out_invoice"
            account_type = "revenue"
        invoice = self.env["account.move"].create(
            {
                "company_id": order.company_id.id,
                "currency_id": order.company_id.currency_id.id,
                "partner_id": partner.id,
                "move_type": move_type,
                "ref": "TESTREC",
                "preferred_payment_method_line_id": order.payment_method_line_id.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "name": "product that cost 100",
                            "account_id": self.company_data[
                                f"default_account_{account_type}"
                            ].id,
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        # Add to payment order
        invoice.create_account_payment_line()
        return invoice

    def test_inbound(self):
        invoice = self.create_invoice_order(self.inbound_order, self.partner)
        invoice2 = self.create_invoice_order(self.inbound_order, self.partner2)
        self.inbound_order.draft2open()
        self.inbound_order.open2generated()
        self.inbound_order.generated2uploaded()
        self.assertEqual(invoice.payment_state, "in_payment")
        self.assertEqual(invoice2.payment_state, "in_payment")
        self.assertEqual(2, len(self.inbound_order.payment_ids))
        self.assertEqual(1, len(self.inbound_order.payment_lot_ids))
        bank_stmt_line = self.stmt_line_model.create(
            {
                "name": "testLine",
                "journal_id": self.bank_journal.id,
                "amount": invoice.amount_total + invoice2.amount_total,
                "date": fields.Date.today(),
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_payment_lot_id = self.inbound_order.payment_lot_ids
        self.assertTrue(bank_stmt_line.can_reconcile)
        bank_stmt_line.reconcile_bank_line()
        self.assertEqual(invoice.payment_state, "paid")
        self.assertEqual(invoice2.payment_state, "paid")

    def test_inbound_unselect(self):
        invoice = self.create_invoice_order(self.inbound_order, self.partner)
        invoice2 = self.create_invoice_order(self.inbound_order, self.partner2)
        self.inbound_order.draft2open()
        self.inbound_order.open2generated()
        self.inbound_order.generated2uploaded()
        self.assertEqual(invoice.payment_state, "in_payment")
        self.assertEqual(invoice2.payment_state, "in_payment")
        self.assertEqual(2, len(self.inbound_order.payment_ids))
        self.assertEqual(1, len(self.inbound_order.payment_lot_ids))
        bank_stmt_line = self.stmt_line_model.create(
            {
                "name": "testLine",
                "journal_id": self.bank_journal.id,
                "amount": invoice.amount_total + invoice2.amount_total,
                "date": fields.Date.today(),
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_payment_lot_id = self.inbound_order.payment_lot_ids
        self.assertTrue(bank_stmt_line.can_reconcile)
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            f.add_payment_lot_id = self.inbound_order.payment_lot_ids
        self.assertFalse(bank_stmt_line.can_reconcile)

    def test_outbound(self):
        invoice = self.create_invoice_order(self.outbound_order, self.partner)
        invoice2 = self.create_invoice_order(self.outbound_order, self.partner2)
        self.outbound_order.draft2open()
        self.outbound_order.open2generated()
        self.outbound_order.generated2uploaded()
        self.assertEqual(invoice.payment_state, "in_payment")
        self.assertEqual(invoice2.payment_state, "in_payment")
        self.assertEqual(2, len(self.outbound_order.payment_ids))
        self.assertEqual(1, len(self.outbound_order.payment_lot_ids))
        bank_stmt_line = self.stmt_line_model.create(
            {
                "name": "testLine",
                "journal_id": self.bank_journal.id,
                "amount": (invoice.amount_total + invoice2.amount_total) * -1,
                "date": fields.Date.today(),
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_payment_lot_id = self.outbound_order.payment_lot_ids
        self.assertTrue(bank_stmt_line.can_reconcile)
        bank_stmt_line.reconcile_bank_line()
        self.assertEqual(invoice.payment_state, "paid")
        self.assertEqual(invoice2.payment_state, "paid")
