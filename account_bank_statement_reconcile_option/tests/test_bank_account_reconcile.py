from datetime import date, timedelta

from odoo.tests.common import TransactionCase


class TestAccountMoveLineSearchFetch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Bank Journal",
                "type": "bank",
                "code": "BNK01",
                "search_limit_days": 0,
            }
        )

        cls.allowed_account = cls.env["account.account"].create(
            {
                "name": "Allowed Account",
                "code": "TST01",
                "account_type": "asset_current",
            }
        )
        cls.other_account = cls.env["account.account"].create(
            {
                "name": "Other Account",
                "code": "TST02",
                "account_type": "asset_current",
            }
        )
        cls.journal.bank_reconcile_account_allowed_ids = [
            (6, 0, [cls.allowed_account.id])
        ]

        cls.statement_line = cls.env["account.bank.statement.line"].create(
            {
                "name": "Statement Line",
                "journal_id": cls.journal.id,
                "amount": 100.0,
                "date": date.today(),
                "payment_ref": "Ref",
                "partner_id": cls.partner.id,
            }
        )

        cls.move = cls.env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": cls.journal.id,
                "date": date.today(),
            }
        )
        cls.move_other = cls.env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": cls.journal.id,
                "date": date.today() - timedelta(days=10),
            }
        )

        # Deactivate move validation if necessary
        ctx = dict(check_move_validity=False)
        cls.move_line_allowed = (
            cls.env["account.move.line"]
            .with_context(**ctx)
            .create(
                {
                    "move_id": cls.move.id,
                    "account_id": cls.allowed_account.id,
                    "debit": 100,
                    "credit": 0,
                }
            )
        )
        cls.move_line_other = (
            cls.env["account.move.line"]
            .with_context(**ctx)
            .create(
                {
                    "move_id": cls.move_other.id,
                    "account_id": cls.other_account.id,
                    "debit": 100,
                    "credit": 0,
                }
            )
        )

    def test_search_fetch_without_context(self):
        res = self.env["account.move.line"].search_fetch([], ["id"])
        ids = [r["id"] for r in res]
        self.assertIn(self.move_line_allowed.id, ids)
        self.assertIn(self.move_line_other.id, ids)

    def test_search_fetch_with_allowed_account_context(self):
        ctx = {
            "bank_statement_reconcile_option_statement_line_id": self.statement_line.id,
        }
        res = self.env["account.move.line"].with_context(**ctx).search_fetch([], ["id"])
        ids = [r["id"] for r in res]
        self.assertIn(self.move_line_allowed.id, ids)
        self.assertNotIn(self.move_line_other.id, ids)

    def test_search_fetch_with_date_limit(self):
        self.journal.search_limit_days = 1

        inside_line = (
            self.env["account.move.line"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "move_id": self.move.id,
                    "account_id": self.allowed_account.id,
                    "debit": 100,
                }
            )
        )
        outside_line = (
            self.env["account.move.line"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "move_id": self.move_other.id,
                    "account_id": self.allowed_account.id,
                    "debit": 200,
                }
            )
        )

        ctx = {
            "bank_statement_reconcile_option_statement_line_id": self.statement_line.id,
        }
        res = self.env["account.move.line"].with_context(**ctx).search_fetch([], ["id"])
        ids = [r["id"] for r in res]
        self.assertIn(inside_line.id, ids)
        self.assertNotIn(outside_line.id, ids)
