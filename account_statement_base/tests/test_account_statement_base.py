from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestOpenEntries(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.company_data["company"]
        cls.acc_bank_stmt_model = cls.env["account.bank.statement"]
        cls.account_move_model = cls.env["account.move"]
        cls.account_move_line_model = cls.env["account.move.line"]
        cls.current_assets_account = cls.env["account.account"].search(
            [
                ("account_type", "=", "asset_current"),
                ("company_ids", "in", cls.company.ids),
            ],
            limit=1,
        )
        cls.current_assets_account.reconcile = True
        cls.non_current_assets_account = cls.env["account.account"].search(
            [
                ("account_type", "=", "asset_non_current"),
                ("company_ids", "in", cls.company.ids),
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

    def test_02_open_statement_lines(self):
        journal = self.company_data["default_journal_bank"]
        statement = self.acc_bank_stmt_model.create(
            {
                "name": "Test Bank Statement",
                "journal_id": journal.id,
                "line_ids": [
                    Command.create(
                        {
                            "date": "2024-01-01",
                            "amount": 100.0,
                            "payment_ref": "Line 1",
                            "journal_id": journal.id,
                        }
                    ),
                ],
            }
        )
        action = statement.action_open_statement_lines()
        self.assertEqual(action["res_model"], "account.bank.statement.line")
        self.assertEqual(action["domain"], [("statement_id", "=", statement.id)])
        self.assertEqual(action["context"]["default_statement_id"], statement.id)
        self.assertEqual(action["context"]["default_journal_id"], journal.id)
        self.assertEqual(
            self.env[action["res_model"]].search(action["domain"]), statement.line_ids
        )

    def test_03_open_journal_entry(self):
        journal = self.company_data["default_journal_bank"]
        line = self.env["account.bank.statement.line"].create(
            {
                "date": "2024-01-01",
                "amount": 100.0,
                "payment_ref": "Line 1",
                "journal_id": journal.id,
            }
        )
        action = line.action_open_journal_entry()
        self.assertEqual(action["res_model"], "account.move")
        self.assertEqual(action["res_id"], line.move_id.id)
