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
        cls.current_assets_account = (
            cls.env["account.account"]
            .search(
                [
                    ("account_type", "=", "asset_current"),
                    ("company_id", "=", cls.company.id),
                ],
                limit=1,
            )
            .copy()
        )
        cls.current_assets_account.reconcile = True
        cls.asset_receivable_account = (
            cls.env["account.account"]
            .search(
                [
                    ("account_type", "=", "asset_receivable"),
                    ("company_id", "=", cls.company.id),
                ],
                limit=1,
            )
            .copy()
        )
        cls.asset_receivable_account.reconcile = True
        cls.equity_account = (
            cls.env["account.account"]
            .search(
                [
                    ("account_type", "=", "equity"),
                    ("company_id", "=", cls.company.id),
                ],
                limit=1,
            )
            .copy()
        )
        cls.non_current_assets_account = (
            cls.env["account.account"]
            .search(
                [
                    ("account_type", "=", "asset_non_current"),
                    ("company_id", "=", cls.company.id),
                ],
                limit=1,
            )
            .copy()
        )
        cls.non_current_assets_account.reconcile = True
        cls.move_1 = cls.env["account.move"].create(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": cls.current_assets_account.id,
                            "name": "DEMO",
                            "credit": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": cls.non_current_assets_account.id,
                            "name": "DEMO",
                            "debit": 100,
                        },
                    ),
                ]
            }
        )
        cls.move_1.action_post()
        cls.move_2 = cls.env["account.move"].create(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": cls.non_current_assets_account.id,
                            "name": "DEMO",
                            "credit": 50,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": cls.equity_account.id,
                            "name": "DEMO",
                            "debit": 50,
                        },
                    ),
                ]
            }
        )
        cls.move_2.action_post()
        cls.move_3 = cls.env["account.move"].create(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": cls.non_current_assets_account.id,
                            "name": "DEMO",
                            "credit": 50,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": cls.equity_account.id,
                            "name": "DEMO",
                            "debit": 50,
                        },
                    ),
                ]
            }
        )
        cls.move_3.action_post()

    def test_reconcile(self):
        account = self.non_current_assets_account
        reconcile_account = self.env["account.account.reconcile"].search(
            [("account_id", "=", account.id)]
        )
        self.assertTrue(reconcile_account)
        with Form(reconcile_account) as f:
            f.add_account_move_line_id = self.move_1.line_ids.filtered(
                lambda r: r.account_id == account
            )
            f.add_account_move_line_id = self.move_2.line_ids.filtered(
                lambda r: r.account_id == account
            )
        reconcile_account.reconcile()
        reconcile_account = self.env["account.account.reconcile"].search(
            [("account_id", "=", account.id)]
        )
        self.assertTrue(reconcile_account)
        with Form(reconcile_account) as f:
            f.add_account_move_line_id = self.move_1.line_ids.filtered(
                lambda r: r.account_id == account
            )
            f.add_account_move_line_id = self.move_3.line_ids.filtered(
                lambda r: r.account_id == account
            )
        reconcile_account.reconcile()
        reconcile_account = self.env["account.account.reconcile"].search(
            [("account_id", "=", account.id)]
        )
        self.assertFalse(reconcile_account)

    def test_clean_reconcile(self):
        account = self.non_current_assets_account
        reconcile_account = self.env["account.account.reconcile"].search(
            [("account_id", "=", account.id)]
        )
        self.assertTrue(reconcile_account)
        with Form(reconcile_account) as f:
            f.add_account_move_line_id = self.move_1.line_ids.filtered(
                lambda r: r.account_id == account
            )
            f.add_account_move_line_id = self.move_2.line_ids.filtered(
                lambda r: r.account_id == account
            )
        self.assertTrue(reconcile_account.reconcile_data_info.get("counterparts"))
        reconcile_account.clean_reconcile()
        self.assertFalse(reconcile_account.reconcile_data_info.get("counterparts"))

    def test_cannot_reconcile(self):
        """
        There is not enough records to reconcile for this account
        """
        reconcile_account = self.env["account.account.reconcile"].search(
            [("account_id", "=", self.current_assets_account.id)]
        )
        self.assertFalse(reconcile_account)

    def test_cannot_reconcile_different_partners(self):
        """
        We can only reconcile lines with the same account and partner.
        """
        reconcile_account = self.env["account.account.reconcile"].search(
            [
                ("account_id", "=", self.asset_receivable_account.id),
            ]
        )
        self.assertFalse(reconcile_account)
        move_1 = self.env["account.move"].create(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": self.current_assets_account.id,
                            "name": "DEMO",
                            "credit": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": self.asset_receivable_account.id,
                            "partner_id": self.env.user.partner_id.id,
                            "name": "DEMO",
                            "debit": 100,
                        },
                    ),
                ]
            }
        )
        move_1.action_post()
        self.env.flush_all()
        move_2 = self.env["account.move"].create(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": self.current_assets_account.id,
                            "name": "DEMO",
                            "debit": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": self.asset_receivable_account.id,
                            "partner_id": self.company.partner_id.id,
                            "name": "DEMO",
                            "credit": 100,
                        },
                    ),
                ]
            }
        )
        move_2.action_post()
        self.env.flush_all()
        reconcile_account = self.env["account.account.reconcile"].search(
            [
                ("account_id", "=", self.asset_receivable_account.id),
            ]
        )
        self.assertFalse(reconcile_account)

        move_3 = self.env["account.move"].create(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": self.current_assets_account.id,
                            "name": "DEMO",
                            "debit": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": self.asset_receivable_account.id,
                            "partner_id": self.env.user.partner_id.id,
                            "name": "DEMO",
                            "credit": 100,
                        },
                    ),
                ]
            }
        )
        move_3.action_post()
        self.env.flush_all()
        reconcile_account = self.env["account.account.reconcile"].search(
            [
                ("account_id", "=", self.asset_receivable_account.id),
            ]
        )
        self.assertTrue(reconcile_account)
        self.assertEqual(reconcile_account.partner_id, self.env.user.partner_id)
