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

    # Testing reconcile action

    def test_reconcile_invoice_currency(self):
        inv1 = self.create_invoice(currency_id=self.currency_usd_id, invoice_amount=100)
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
                "amount": 50,
                "amount_currency": 100,
                "foreign_currency_id": self.currency_usd_id,
                "date": time.strftime("%Y-07-15"),
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_account_move_line_id = inv1.line_ids.filtered(
                lambda l: l.account_id.account_type == "asset_receivable"
            )
            self.assertFalse(f.add_account_move_line_id)
            self.assertTrue(f.can_reconcile)

    def test_reconcile_invoice_reconcile_full(self):
        """
        We want to test the reconcile widget for bank statements on invoices.
        As we use edit mode by default, we will also check what happens when
        we press unreconcile
        """
        inv1 = self.create_invoice(
            currency_id=self.currency_euro_id, invoice_amount=100
        )
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
                "amount": 50,
                "date": time.strftime("%Y-07-15"),
            }
        )
        receivable1 = inv1.line_ids.filtered(
            lambda l: l.account_id.account_type == "asset_receivable"
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_account_move_line_id = receivable1
            self.assertFalse(f.add_account_move_line_id)
            self.assertTrue(f.can_reconcile)
            f.manual_reference = "account.move.line;%s" % receivable1.id
            self.assertEqual(-50, f.manual_amount)
        self.assertEqual(2, len(bank_stmt_line.reconcile_data_info["data"]))
        bank_stmt_line.button_manual_reference_full_paid()
        self.assertEqual(3, len(bank_stmt_line.reconcile_data_info["data"]))
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            f.manual_reference = "account.move.line;%s" % receivable1.id
            self.assertEqual(-100, f.manual_amount)

    def test_reconcile_invoice_unreconcile(self):
        """
        We want to test the reconcile widget for bank statements on invoices.
        As we use edit mode by default, we will also check what happens when
        we press unreconcile
        """
        inv1 = self.create_invoice(
            currency_id=self.currency_euro_id, invoice_amount=100
        )
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
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_account_move_line_id = inv1.line_ids.filtered(
                lambda l: l.account_id.account_type == "asset_receivable"
            )
            self.assertFalse(f.add_account_move_line_id)
            self.assertTrue(f.can_reconcile)
        self.assertFalse(bank_stmt_line.is_reconciled)
        self.assertTrue(
            bank_stmt_line.move_id.line_ids.filtered(
                lambda r: r.account_id == self.bank_journal_euro.suspense_account_id
            )
        )
        number_of_lines = len(bank_stmt_line.reconcile_data_info["data"])
        bank_stmt_line.reconcile_bank_line()
        self.assertEqual(
            number_of_lines, len(bank_stmt_line.reconcile_data_info["data"])
        )
        self.assertTrue(bank_stmt_line.is_reconciled)
        self.assertFalse(
            bank_stmt_line.move_id.line_ids.filtered(
                lambda r: r.account_id == self.bank_journal_euro.suspense_account_id
            )
        )
        bank_stmt_line.unreconcile_bank_line()
        self.assertFalse(bank_stmt_line.is_reconciled)
        self.assertTrue(
            bank_stmt_line.move_id.line_ids.filtered(
                lambda r: r.account_id == self.bank_journal_euro.suspense_account_id
            )
        )

    def test_reconcile_invoice_partial(self):
        """
        We want to partially reconcile two invoices from a single payment.
        As a result, both invoices must be partially reconciled
        """
        inv1 = self.create_invoice(
            currency_id=self.currency_euro_id, invoice_amount=100
        )
        inv2 = self.create_invoice(
            currency_id=self.currency_euro_id, invoice_amount=100
        )
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
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        receivable1 = inv1.line_ids.filtered(
            lambda l: l.account_id.account_type == "asset_receivable"
        )
        receivable2 = inv2.line_ids.filtered(
            lambda l: l.account_id.account_type == "asset_receivable"
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_account_move_line_id = receivable1
            self.assertFalse(f.add_account_move_line_id)
            self.assertTrue(f.can_reconcile)
            f.manual_reference = "account.move.line;%s" % receivable1.id
            self.assertEqual(f.manual_amount, -100)
            f.manual_amount = -70
            self.assertFalse(f.can_reconcile)
            f.add_account_move_line_id = receivable2
            f.manual_reference = "account.move.line;%s" % receivable2.id
            self.assertEqual(f.manual_amount, -30)
            self.assertTrue(f.can_reconcile)
        self.assertEqual(inv1.amount_residual_signed, 100)
        self.assertEqual(inv2.amount_residual_signed, 100)
        number_of_lines = len(bank_stmt_line.reconcile_data_info["data"])
        bank_stmt_line.reconcile_bank_line()
        self.assertEqual(
            number_of_lines, len(bank_stmt_line.reconcile_data_info["data"])
        )
        self.assertEqual(inv1.amount_residual_signed, 30)
        self.assertEqual(inv2.amount_residual_signed, 70)

    def test_reconcile_invoice_partial_supplier(self):
        """
        We want to partially reconcile two invoices from a single payment.
        As a result, both invoices must be partially reconciled
        """
        inv1 = self.create_invoice(
            currency_id=self.currency_euro_id,
            invoice_amount=100,
            move_type="in_invoice",
        )
        inv2 = self.create_invoice(
            currency_id=self.currency_euro_id,
            invoice_amount=100,
            move_type="in_invoice",
        )
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
                "amount": -100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        receivable1 = inv1.line_ids.filtered(
            lambda l: l.account_id.account_type == "liability_payable"
        )
        receivable2 = inv2.line_ids.filtered(
            lambda l: l.account_id.account_type == "liability_payable"
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_account_move_line_id = receivable1
            self.assertFalse(f.add_account_move_line_id)
            self.assertTrue(f.can_reconcile)
            f.manual_reference = "account.move.line;%s" % receivable1.id
            self.assertEqual(f.manual_amount, 100)
            f.manual_amount = 70
            self.assertFalse(f.can_reconcile)
            f.add_account_move_line_id = receivable2
            f.manual_reference = "account.move.line;%s" % receivable2.id
            self.assertEqual(f.manual_amount, 30)
            self.assertTrue(f.can_reconcile)
        self.assertEqual(inv1.amount_residual_signed, -100)
        self.assertEqual(inv2.amount_residual_signed, -100)
        number_of_lines = len(bank_stmt_line.reconcile_data_info["data"])
        bank_stmt_line.reconcile_bank_line()
        self.assertEqual(
            number_of_lines, len(bank_stmt_line.reconcile_data_info["data"])
        )
        self.assertEqual(inv1.amount_residual_signed, -30)
        self.assertEqual(inv2.amount_residual_signed, -70)

    def test_reconcile_model(self):
        """
        We want to test what happens when we select an reconcile model to fill a
        bank statement.
        """
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
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.manual_model_id = self.rule
            self.assertTrue(f.can_reconcile)
        number_of_lines = len(bank_stmt_line.reconcile_data_info["data"])
        bank_stmt_line.reconcile_bank_line()
        self.assertEqual(
            number_of_lines, len(bank_stmt_line.reconcile_data_info["data"])
        )
        self.assertEqual(2, len(bank_stmt_line.move_id.line_ids))
        self.assertTrue(
            bank_stmt_line.move_id.line_ids.filtered(
                lambda r: r.account_id == self.current_assets_account
            )
        )

    def test_reconcile_model_tax_included(self):
        """
        We want to test what happens when we select an reconcile model to fill a
        bank statement.
        """
        self.rule.line_ids.write(
            {"tax_ids": [(4, self.tax_10.id)], "force_tax_included": True}
        )
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
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.manual_model_id = self.rule
            self.assertTrue(f.can_reconcile)
        number_of_lines = len(bank_stmt_line.reconcile_data_info["data"])
        bank_stmt_line.reconcile_bank_line()
        self.assertEqual(
            number_of_lines, len(bank_stmt_line.reconcile_data_info["data"])
        )
        self.assertEqual(3, len(bank_stmt_line.move_id.line_ids))
        self.assertTrue(
            bank_stmt_line.move_id.line_ids.filtered(
                lambda r: r.account_id == self.current_assets_account
                and r.tax_ids == self.tax_10
            )
        )
        self.assertTrue(
            bank_stmt_line.move_id.line_ids.filtered(
                lambda r: r.tax_line_id == self.tax_10
            )
        )

    def test_reconcile_invoice_model(self):
        """
        We want to test what happens when we select a reconcile model to fill a
        bank statement prefilled with an invoice.

        The result should be the reconcile of the invoice, and the rest set to the model
        """

        inv1 = self.create_invoice(currency_id=self.currency_euro_id)

        receivable1 = inv1.line_ids.filtered(
            lambda l: l.account_id.account_type == "asset_receivable"
        )
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
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_account_move_line_id = receivable1
            self.assertFalse(f.can_reconcile)
            f.manual_model_id = self.rule
            self.assertTrue(f.can_reconcile)
        number_of_lines = len(bank_stmt_line.reconcile_data_info["data"])
        bank_stmt_line.reconcile_bank_line()
        self.assertEqual(
            number_of_lines, len(bank_stmt_line.reconcile_data_info["data"])
        )
        self.assertNotEqual(self.current_assets_account, receivable1.account_id)
        self.assertTrue(
            bank_stmt_line.move_id.line_ids.filtered(
                lambda r: r.account_id == self.current_assets_account
            )
        )
        self.assertTrue(
            bank_stmt_line.move_id.line_ids.filtered(
                lambda r: r.account_id == receivable1.account_id
            )
        )
        self.assertEqual(0, inv1.amount_residual)

    def test_reconcile_rule_on_create(self):
        """
        Testing the fill of the bank statment line with
        writeoff suggestion reconcile model with auto_reconcile
        """
        self.env["account.reconcile.model"].create(
            {
                "name": "write-off model suggestion",
                "rule_type": "writeoff_suggestion",
                "match_label": "contains",
                "match_label_param": "DEMO WRITEOFF",
                "auto_reconcile": True,
                "line_ids": [(0, 0, {"account_id": self.current_assets_account.id})],
            }
        )

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
                "name": "DEMO WRITEOFF",
                "payment_ref": "DEMO WRITEOFF",
                "journal_id": self.bank_journal_euro.id,
                "statement_id": bank_stmt.id,
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        self.assertTrue(bank_stmt_line.is_reconciled)

    def test_reconcile_invoice_keep(self):
        """
        We want to test how the keep mode works, keeping the original move lines.
        When unreconciling, the entry created for the reconciliation is reversed.
        """
        self.bank_journal_euro.reconcile_mode = "keep"
        self.bank_journal_euro.suspense_account_id.reconcile = True
        inv1 = self.create_invoice(
            currency_id=self.currency_euro_id, invoice_amount=100
        )
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
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        receivable1 = inv1.line_ids.filtered(
            lambda l: l.account_id.account_type == "asset_receivable"
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_account_move_line_id = receivable1
            self.assertFalse(f.add_account_move_line_id)
        self.assertTrue(bank_stmt_line.can_reconcile)
        number_of_lines = len(bank_stmt_line.reconcile_data_info["data"])
        bank_stmt_line.reconcile_bank_line()
        self.assertEqual(
            number_of_lines, len(bank_stmt_line.reconcile_data_info["data"])
        )
        self.assertIn(
            self.bank_journal_euro.suspense_account_id,
            bank_stmt_line.mapped("move_id.line_ids.account_id"),
        )
        # Reset reconciliation
        reconcile_move = (
            bank_stmt_line.line_ids._all_reconciled_lines()
            .filtered(lambda line: line.move_id != bank_stmt_line.move_id)
            .move_id
        )
        bank_stmt_line.unreconcile_bank_line()
        self.assertTrue(reconcile_move.reversal_move_id)
        self.assertFalse(bank_stmt_line.is_reconciled)

    # Testing to check functionality

    def test_reconcile_invoice_to_check_reconciled(self):
        """
        We want to test the reconcile widget for bank statements on invoices.
        As we use edit mode by default, we will also check what happens when
        we press unreconcile
        """
        inv1 = self.create_invoice(
            currency_id=self.currency_euro_id, invoice_amount=100
        )
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
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        receivable1 = inv1.line_ids.filtered(
            lambda l: l.account_id.account_type == "asset_receivable"
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_account_move_line_id = receivable1
            self.assertTrue(f.can_reconcile)
        self.assertFalse(bank_stmt_line.is_reconciled)
        self.assertFalse(bank_stmt_line.to_check)
        bank_stmt_line.action_to_check()
        self.assertTrue(bank_stmt_line.is_reconciled)
        self.assertTrue(bank_stmt_line.to_check)
        bank_stmt_line.action_checked()
        self.assertTrue(bank_stmt_line.is_reconciled)
        self.assertFalse(bank_stmt_line.to_check)

    def test_reconcile_invoice_to_check_not_reconciled(self):
        """
        We want to test the reconcile widget for bank statements on invoices.
        As we use edit mode by default, we will also check what happens when
        we press unreconcile
        """
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
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        self.assertFalse(bank_stmt_line.is_reconciled)
        self.assertFalse(bank_stmt_line.to_check)
        bank_stmt_line.action_to_check()
        self.assertFalse(bank_stmt_line.is_reconciled)
        self.assertTrue(bank_stmt_line.to_check)
        bank_stmt_line.action_checked()
        self.assertFalse(bank_stmt_line.is_reconciled)
        self.assertFalse(bank_stmt_line.to_check)

    # Testing widget

    def test_widget_invoice_clean(self):
        """
        We want to test how the clean works on an already defined bank statement
        """
        inv1 = self.create_invoice(
            currency_id=self.currency_euro_id, invoice_amount=100
        )
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
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        receivable1 = inv1.line_ids.filtered(
            lambda l: l.account_id.account_type == "asset_receivable"
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_account_move_line_id = receivable1
            self.assertFalse(f.add_account_move_line_id)
        self.assertTrue(bank_stmt_line.can_reconcile)
        bank_stmt_line.clean_reconcile()
        self.assertFalse(bank_stmt_line.can_reconcile)

    def test_widget_invoice_delete(self):
        """
        We need to test the possibility to remove a line from the reconcile widget
        """
        inv1 = self.create_invoice(
            currency_id=self.currency_euro_id, invoice_amount=100
        )
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
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        receivable1 = inv1.line_ids.filtered(
            lambda l: l.account_id.account_type == "asset_receivable"
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_account_move_line_id = receivable1
            self.assertFalse(f.add_account_move_line_id)
            self.assertTrue(f.can_reconcile)
            f.manual_reference = "account.move.line;%s" % receivable1.id
            self.assertEqual(f.manual_amount, -100)
            f.manual_delete = True
            self.assertFalse(f.can_reconcile)

    def test_widget_invoice_unselect(self):
        """
        We want to test how selection and unselection of an account move lines is managed
        by the system.
        """
        inv1 = self.create_invoice(
            currency_id=self.currency_euro_id, invoice_amount=100
        )
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
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_account_move_line_id = inv1.line_ids.filtered(
                lambda l: l.account_id.account_type == "asset_receivable"
            )
            self.assertFalse(f.add_account_move_line_id)
            self.assertTrue(f.can_reconcile)
            f.add_account_move_line_id = inv1.line_ids.filtered(
                lambda l: l.account_id.account_type == "asset_receivable"
            )
            self.assertFalse(f.add_account_move_line_id)
            self.assertFalse(f.can_reconcile)

    def test_widget_invoice_change_partner(self):
        """
        We want to know how the change of partner of
        a bank statement line is managed
        """
        inv1 = self.create_invoice(
            currency_id=self.currency_euro_id, invoice_amount=100
        )
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
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        liquidity_lines, suspense_lines, other_lines = bank_stmt_line._seek_for_lines()
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            self.assertFalse(f.partner_id)
            f.manual_reference = "account.move.line;%s" % liquidity_lines.id
            f.manual_partner_id = inv1.partner_id
            self.assertEqual(f.partner_id, inv1.partner_id)
        bank_stmt_line.clean_reconcile()
        # As we have a set a partner, the cleaning should assign the invoice automatically
        self.assertTrue(bank_stmt_line.can_reconcile)

    def test_widget_model_clean(self):
        """
        We want to test what happens when we select an reconcile model to fill a
        bank statement.
        """
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
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.manual_model_id = self.rule
            self.assertTrue(f.can_reconcile)
            # We need to check what happens when we uncheck it too
            f.manual_model_id = self.env["account.reconcile.model"]
            self.assertFalse(f.can_reconcile)
            f.manual_model_id = self.rule
            self.assertTrue(f.can_reconcile)

    # Testing actions

    def test_bank_statement_rainbowman(self):
        message = self.bank_journal_euro.get_rainbowman_message()
        self.assertTrue(message)
        self.acc_bank_stmt_line_model.create(
            {
                "name": "testLine",
                "journal_id": self.bank_journal_euro.id,
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        self.env.flush_all()
        message = self.bank_journal_euro.get_rainbowman_message()
        self.assertFalse(message)

    def test_bank_statement_line_actions(self):
        """
        Testing the actions of bank statement
        """
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
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        move_action = bank_stmt_line.action_show_move()
        self.assertEqual(
            bank_stmt_line.move_id,
            self.env[move_action["res_model"]].browse(move_action["res_id"]),
        )

    # Testing filters

    def test_filter_partner(self):
        """
        When a partner is set, the system might try to define an existent
        invoice automatically
        """
        inv1 = self.create_invoice(currency_id=self.currency_euro_id)
        inv2 = self.create_invoice(currency_id=self.currency_euro_id)
        partner = inv1.partner_id

        receivable1 = inv1.line_ids.filtered(
            lambda l: l.account_id.account_type == "asset_receivable"
        )
        self.assertTrue(receivable1)
        receivable2 = inv2.line_ids.filtered(
            lambda l: l.account_id.account_type == "asset_receivable"
        )
        self.assertTrue(receivable2)

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
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )

        # Without a partner set, No default data

        bkstmt_data = bank_stmt_line.reconcile_data_info
        mv_lines_ids = bkstmt_data["counterparts"]
        self.assertNotIn(receivable1.id, mv_lines_ids)
        self.assertNotIn(receivable2.id, mv_lines_ids)

        # This is like input a partner in the widget

        bank_stmt_line.partner_id = partner
        bank_stmt_line.flush_recordset()
        bank_stmt_line.invalidate_recordset()
        bkstmt_data = bank_stmt_line.reconcile_data_info
        mv_lines_ids = bkstmt_data["counterparts"]

        self.assertIn(receivable1.id, mv_lines_ids)
        self.assertIn(receivable2.id, mv_lines_ids)

        # With a partner set, type the invoice reference in the filter
        bank_stmt_line.payment_ref = inv1.payment_reference
        bank_stmt_line.flush_recordset()
        bank_stmt_line.invalidate_recordset()
        bkstmt_data = bank_stmt_line.reconcile_data_info
        mv_lines_ids = bkstmt_data["counterparts"]

        self.assertIn(receivable1.id, mv_lines_ids)
        self.assertNotIn(receivable2.id, mv_lines_ids)

    def test_partner_name_with_parent(self):
        parent_partner = self.env["res.partner"].create(
            {
                "name": "test",
            }
        )
        child_partner = self.env["res.partner"].create(
            {
                "name": "test",
                "parent_id": parent_partner.id,
                "type": "delivery",
            }
        )
        self.create_invoice_partner(
            currency_id=self.currency_euro_id, partner_id=child_partner.id
        )

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
                "statement_id": bank_stmt.id,
                "journal_id": self.bank_journal_euro.id,
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
                "payment_ref": "test",
                "partner_name": "test",
            }
        )

        bkstmt_data = bank_stmt_line.reconcile_data_info
        self.assertEqual(len(bkstmt_data["counterparts"]), 1)
        self.assertEqual(
            self.env["account.move.line"]
            .browse(bkstmt_data["counterparts"])
            .partner_id,
            parent_partner,
        )

    def test_journal_foreign_currency(self):
        inv1 = self.create_invoice(currency_id=self.currency_usd_id, invoice_amount=100)
        bank_stmt = self.acc_bank_stmt_model.create(
            {
                "company_id": self.env.ref("base.main_company").id,
                "journal_id": self.bank_journal_usd.id,
                "date": time.strftime("%Y-07-15"),
                "name": "test",
            }
        )
        bank_stmt_line = self.acc_bank_stmt_line_model.create(
            {
                "name": "testLine",
                "journal_id": self.bank_journal_usd.id,
                "statement_id": bank_stmt.id,
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_account_move_line_id = inv1.line_ids.filtered(
                lambda l: l.account_id.account_type == "asset_receivable"
            )
            self.assertFalse(f.add_account_move_line_id)
            self.assertTrue(f.can_reconcile)
        self.assertTrue(bank_stmt_line.can_reconcile)
        number_of_lines = len(bank_stmt_line.reconcile_data_info["data"])
        bank_stmt_line.reconcile_bank_line()
        self.assertEqual(
            number_of_lines, len(bank_stmt_line.reconcile_data_info["data"])
        )
        self.assertEqual(0, inv1.amount_residual)
        self.assertTrue(
            inv1.line_ids.filtered(
                lambda line: line.account_id.account_type == "asset_receivable"
            ).full_reconcile_id
        )

    def test_journal_foreign_currency_change(self):
        self.env["res.currency.rate"].create(
            {
                "currency_id": self.env.ref("base.EUR").id,
                "name": time.strftime("%Y-07-14"),
                "rate": 1.15,
            }
        )
        bank_stmt = self.acc_bank_stmt_model.create(
            {
                "company_id": self.env.ref("base.main_company").id,
                "journal_id": self.bank_journal_usd.id,
                "date": time.strftime("%Y-07-15"),
                "name": "test",
            }
        )
        bank_stmt_line = self.acc_bank_stmt_line_model.create(
            {
                "name": "testLine",
                "journal_id": self.bank_journal_usd.id,
                "statement_id": bank_stmt.id,
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            line = f.reconcile_data_info["data"][0]
            self.assertEqual(
                line["currency_amount"],
                100,
            )
        self.env["res.currency.rate"].create(
            {
                "currency_id": self.env.ref("base.EUR").id,
                "name": time.strftime("%Y-07-15"),
                "rate": 1.2,
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            line = f.reconcile_data_info["data"][0]
            self.assertEqual(
                line["currency_amount"],
                100,
            )

    def test_invoice_foreign_currency_change(self):
        self.env["res.currency.rate"].create(
            {
                "currency_id": self.env.ref("base.EUR").id,
                "name": time.strftime("%Y-07-14"),
                "rate": 1.15,
            }
        )
        self.env["res.currency.rate"].create(
            {
                "currency_id": self.env.ref("base.EUR").id,
                "name": time.strftime("%Y-07-15"),
                "rate": 1.2,
            }
        )
        inv1 = self._create_invoice(
            currency_id=self.currency_usd_id,
            invoice_amount=100,
            date_invoice="2021-07-14",
            auto_validate=True,
        )
        bank_stmt = self.acc_bank_stmt_model.create(
            {
                "company_id": self.env.ref("base.main_company").id,
                "journal_id": self.bank_journal_usd.id,
                "date": time.strftime("%Y-07-15"),
                "name": "test",
            }
        )
        bank_stmt_line = self.acc_bank_stmt_line_model.create(
            {
                "name": "testLine",
                "journal_id": self.bank_journal_usd.id,
                "statement_id": bank_stmt.id,
                "amount": 100,
                "date": time.strftime("%Y-07-15"),
            }
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            line = f.reconcile_data_info["data"][0]
            self.assertEqual(
                line["currency_amount"],
                100,
            )
            f.add_account_move_line_id = inv1.line_ids.filtered(
                lambda l: l.account_id.account_type == "asset_receivable"
            )
            self.assertFalse(f.add_account_move_line_id)
            self.assertTrue(f.can_reconcile)
            self.assertEqual(3, len(f.reconcile_data_info["data"]))
