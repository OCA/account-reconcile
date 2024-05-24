from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import TestAccountReconciliationCommon


@tagged("post_install", "-at_install")
class TestReconciliationWidget(TestAccountReconciliationCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.acc_bank_stmt_model = cls.env["account.bank.statement"]
        cls.account_move_model = cls.env["account.move"]
        cls.account_move_line_model = cls.env["account.move.line"]
        cls.current_assets_account = cls.env["account.account"].search(
            [
                ("account_type", "=", "asset_current"),
                ("company_id", "=", cls.company.id),
            ],
            limit=1,
        )
        cls.current_assets_account.reconcile = True
        cls.non_current_assets_account = cls.env["account.account"].search(
            [
                ("account_type", "=", "asset_non_current"),
                ("company_id", "=", cls.company.id),
            ],
            limit=1,
        )
        cls.non_current_assets_account.reconcile = True

    def test_01_test_open_entries(self):
        move = self.account_move_model.create(
            {
                "line_ids": [
                    Command.create(
                        {
                            "account_id": self.current_assets_account.id,
                            "name": "DEMO",
                            "credit": 100,
                        }
                    ),
                    Command.create(
                        {
                            "account_id": self.non_current_assets_account.id,
                            "name": "DEMO",
                            "debit": 100,
                        }
                    ),
                ]
            }
        )
        move.action_post()
        statement = self.acc_bank_stmt_model.create(
            {
                "name": "Test Bank Statement",
                "line_ids": [
                    Command.create(
                        {
                            "date": "2024-01-01",
                            "amount": 100.0,
                            "payment_ref": move.name,
                            "line_ids": [Command.set([move.line_ids[0].id])],
                        }
                    ),
                    Command.create(
                        {
                            "date": "2024-01-01",
                            "amount": 100.0,
                            "payment_ref": move.name,
                            "line_ids": [Command.set([move.line_ids[1].id])],
                        }
                    ),
                ],
            }
        )
        domain = [
            "&",
            ("parent_state", "=", "posted"),
            ("statement_id", "=", statement.id),
        ]
        result = statement.open_entries()
        move_lines = self.env[result["res_model"]].search(result["domain"])
        self.assertTrue(result)
        self.assertEqual(result.get("res_model"), "account.move.line")
        self.assertEqual(result.get("context").get("search_default_group_by_move"), 1)
        self.assertEqual(result.get("context").get("expand"), 1)
        self.assertEqual(result.get("domain"), domain)
        self.assertIn(statement.line_ids.line_ids[0], move_lines)
        self.assertIn(statement.line_ids.line_ids[1], move_lines)
