# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestStatementReconcileStatus(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bank_journal = cls.company_data["default_journal_bank"]
        cls.bank_journal.suspense_account_id.reconcile = True
        cls.expense_account = cls.company_data["default_account_expense"]

    def _create_statement_with_lines(self, amounts):
        st = self.env["account.bank.statement"].create(
            {"journal_id": self.bank_journal.id}
        )
        for amount in amounts:
            line = self.env["account.bank.statement.line"].create(
                {
                    "journal_id": self.bank_journal.id,
                    "statement_id": st.id,
                    "amount": amount,
                    "date": "2026-01-01",
                    "payment_ref": f"Line {amount}",
                }
            )
            if line.state != "posted":
                line.move_id.action_post()
        return st

    def _reconcile_st_line(self, st_line):
        _liquidity, suspense, _other = st_line._seek_for_lines()
        if not suspense:
            return
        st_line.move_id.checked = True
        counter_move = self.env["account.move"].create(
            {
                "journal_id": self.bank_journal.id,
                "line_ids": [
                    Command.create(
                        {
                            "account_id": suspense[0].account_id.id,
                            "debit": sum(suspense.mapped("credit")),
                            "credit": sum(suspense.mapped("debit")),
                        }
                    ),
                    Command.create(
                        {
                            "account_id": self.expense_account.id,
                            "debit": sum(suspense.mapped("debit")),
                            "credit": sum(suspense.mapped("credit")),
                        }
                    ),
                ],
            }
        )
        counter_move.action_post()
        counter_line = counter_move.line_ids.filtered(
            lambda line: line.account_id == suspense[0].account_id
        )
        (suspense + counter_line).reconcile()

    def _unreconcile_st_line(self, st_line):
        _liquidity, suspense, _other = st_line._seek_for_lines()
        if suspense:
            suspense.remove_move_reconcile()

    def test_full_reconciliation_lifecycle(self):
        st = self._create_statement_with_lines([100, 200, 300])
        line1, line2, line3 = st.line_ids.sorted("amount")
        self.assertEqual(st.reconcile_state, "not_started")
        self.assertFalse(st.date_first_fully_reconciled)
        self._reconcile_st_line(line1)
        self.assertEqual(st.reconcile_state, "in_progress")
        self.assertFalse(st.date_first_fully_reconciled)
        self._reconcile_st_line(line2)
        self.assertEqual(st.reconcile_state, "in_progress")
        self.assertFalse(st.date_first_fully_reconciled)
        self._reconcile_st_line(line3)
        self.assertEqual(st.reconcile_state, "done")
        date_done = st.date_first_fully_reconciled
        self.assertTrue(date_done)
        self._unreconcile_st_line(line2)
        self.assertEqual(st.reconcile_state, "in_progress")
        self.assertEqual(st.date_first_fully_reconciled, date_done)
        self._reconcile_st_line(line2)
        self.assertEqual(st.reconcile_state, "done")
        self.assertEqual(st.date_first_fully_reconciled, date_done)
