import time

from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import TestAccountReconciliationCommon


@tagged("post_install", "-at_install")
class TestReconciliationWidget(TestAccountReconciliationCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.acc_bank_stmt_model = cls.env["account.bank.statement"]
        cls.acc_bank_stmt_line_model = cls.env["account.bank.statement.line"]
        cls.bank_journal_usd.suspense_account_id = (
            cls.company.account_journal_suspense_account_id
        )
        cls.bank_journal_euro.suspense_account_id = (
            cls.company.account_journal_suspense_account_id
        )
        cls.current_assets_account = cls.env["account.account"].search(
            [
                ("account_type", "=", "asset_current"),
                ("company_id", "=", cls.company.id),
            ],
            limit=1,
        )
        cls.current_assets_account.reconcile = True

        cls.rule = cls.env["account.reconcile.model"].create(
            {
                "name": "write-off model",
                "rule_type": "writeoff_button",
                "match_partner": True,
                "match_partner_ids": [],
                "line_ids": [(0, 0, {"account_id": cls.current_assets_account.id})],
            }
        )
        cls.tax_10 = cls.env["account.tax"].create(
            {
                "name": "tax_10",
                "amount_type": "percent",
                "amount": 10.0,
            }
        )
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
        cls.inbound_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test Direct Debit of customers",
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "company_id": cls.company.id,
            }
        )
        cls.inbound_order = cls.env["account.payment.order"].create(
            {
                "payment_type": "inbound",
                "payment_mode_id": cls.inbound_mode.id,
                "journal_id": cls.bank_journal_usd.id,
            }
        )
        cls.outbound_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test Direct Debit of customers",
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
                "company_id": cls.company.id,
            }
        )
        cls.outbound_order = cls.env["account.payment.order"].create(
            {
                "payment_type": "outbound",
                "payment_mode_id": cls.outbound_mode.id,
                "journal_id": cls.bank_journal_usd.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "other partner"})

    def create_invoice_order(self, order, partner_id=False):
        # Create invoice
        move_type = "in_invoice"
        if order.payment_type == "inbound":
            move_type = "out_invoice"
        invoice = self._create_invoice(
            move_type=move_type,
            partner_id=partner_id,
            invoice_amount=100,
            auto_validate=True,
        )
        # Add to payment order using the
        invoice.payment_mode_id = order.payment_mode_id
        invoice.ref = "My Reference"
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=invoice.ids
        ).create({}).run()
        return invoice

    def test_inbound(self):
        invoice = self.create_invoice_order(self.inbound_order)
        invoice2 = self.create_invoice_order(
            self.inbound_order, partner_id=self.partner.id
        )
        self.inbound_order.draft2open()
        self.inbound_order.open2generated()
        self.inbound_order.generated2uploaded()
        self.assertEqual(invoice.payment_state, "in_payment")
        self.assertEqual(invoice2.payment_state, "in_payment")
        self.assertEqual(2, len(self.inbound_order.payment_ids))
        self.assertEqual(1, len(self.inbound_order.maturity_order_ids))
        bank_stmt = self.acc_bank_stmt_model.create(
            {
                "company_id": self.env.ref("base.main_company").id,
                "journal_id": self.bank_journal_euro.id,
                "date": time.strftime("%Y-07-15"),
                "name": "test",
            }
        )
        bank_stmt_line = self.acc_bank_stmt_line_model.create(
            {
                "name": "testLine",
                "journal_id": self.bank_journal_euro.id,
                "statement_id": bank_stmt.id,
                "amount": 200,
                "date": time.strftime("%Y-07-15"),
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_payment_order_id = self.inbound_order.maturity_order_ids
        self.assertTrue(bank_stmt_line.can_reconcile)
        self.assertTrue(bank_stmt_line.can_reconcile)
        bank_stmt_line.reconcile_bank_line()
        self.assertEqual(invoice.payment_state, "paid")
        self.assertEqual(invoice2.payment_state, "paid")

    def test_inbound_unselect(self):
        invoice = self.create_invoice_order(self.inbound_order)
        invoice2 = self.create_invoice_order(
            self.inbound_order, partner_id=self.partner.id
        )
        self.inbound_order.draft2open()
        self.inbound_order.open2generated()
        self.inbound_order.generated2uploaded()
        self.assertEqual(invoice.payment_state, "in_payment")
        self.assertEqual(invoice2.payment_state, "in_payment")
        self.assertEqual(2, len(self.inbound_order.payment_ids))
        self.assertEqual(1, len(self.inbound_order.maturity_order_ids))
        bank_stmt = self.acc_bank_stmt_model.create(
            {
                "company_id": self.env.ref("base.main_company").id,
                "journal_id": self.bank_journal_euro.id,
                "date": time.strftime("%Y-07-15"),
                "name": "test",
            }
        )
        bank_stmt_line = self.acc_bank_stmt_line_model.create(
            {
                "name": "testLine",
                "journal_id": self.bank_journal_euro.id,
                "statement_id": bank_stmt.id,
                "amount": 200,
                "date": time.strftime("%Y-07-15"),
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_payment_order_id = self.inbound_order.maturity_order_ids
        self.assertTrue(bank_stmt_line.can_reconcile)
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            f.add_payment_order_id = self.inbound_order.maturity_order_ids
        self.assertFalse(bank_stmt_line.can_reconcile)

    def test_outbound(self):
        invoice = self.create_invoice_order(self.outbound_order)
        invoice2 = self.create_invoice_order(
            self.outbound_order, partner_id=self.partner.id
        )
        self.outbound_order.draft2open()
        self.outbound_order.open2generated()
        self.outbound_order.generated2uploaded()
        self.assertEqual(invoice.payment_state, "in_payment")
        self.assertEqual(invoice2.payment_state, "in_payment")
        self.assertEqual(2, len(self.outbound_order.payment_ids))
        self.assertEqual(1, len(self.outbound_order.maturity_order_ids))
        bank_stmt = self.acc_bank_stmt_model.create(
            {
                "company_id": self.env.ref("base.main_company").id,
                "journal_id": self.bank_journal_euro.id,
                "date": time.strftime("%Y-07-15"),
                "name": "test",
            }
        )
        bank_stmt_line = self.acc_bank_stmt_line_model.create(
            {
                "name": "testLine",
                "journal_id": self.bank_journal_euro.id,
                "statement_id": bank_stmt.id,
                "amount": -200,
                "date": time.strftime("%Y-07-15"),
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_payment_order_id = self.outbound_order.maturity_order_ids
        self.assertTrue(bank_stmt_line.can_reconcile)
        bank_stmt_line.reconcile_bank_line()
        self.assertEqual(invoice.payment_state, "paid")
        self.assertEqual(invoice2.payment_state, "paid")
