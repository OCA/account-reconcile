# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAccountMoveReconcileHelper(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AccountObj = cls.env["account.account"]
        cls.AccountJournalObj = cls.env["account.journal"]
        cls.AccountMoveObj = cls.env["account.move"]
        cls.AccountMoveLineObj = cls.env["account.move.line"]

        cls.account_recv = cls.AccountObj.create(
            {
                "code": "MRH.RECVT",
                "name": "Receivable (test)",
                "reconcile": True,
                "account_type": "asset_receivable",
            }
        )
        cls.account_sale = cls.AccountObj.create(
            {
                "code": "MRH.SALET",
                "name": "Receivable (sale)",
                "reconcile": True,
                "account_type": "income",
            }
        )

        cls.sales_journal = cls.AccountJournalObj.create(
            {
                "name": "Sales journal",
                "code": "MRH-SAJT",
                "type": "sale",
                "default_account_id": cls.account_sale.id,
            }
        )

    def create_account_move(self, amount, debit_account, credit_account):
        return self.AccountMoveObj.create(
            {
                "journal_id": self.sales_journal.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Receivable line",
                            "account_id": debit_account.id,
                            "debit": amount,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Sales line",
                            "account_id": credit_account.id,
                            "credit": amount,
                        },
                    ),
                ],
            }
        )

    def test_01_partial_reconcile(self):
        base_move = self.create_account_move(5000, self.account_recv, self.account_sale)

        move1 = self.create_account_move(1000, self.account_sale, self.account_recv)

        move2 = self.create_account_move(1000, self.account_sale, self.account_recv)

        lines = self.AccountMoveLineObj.search(
            [
                ("move_id", "in", [base_move.id, move1.id, move2.id]),
                ("account_id", "=", self.account_recv.id),
            ]
        )
        lines.mapped("move_id").action_post()
        lines.reconcile()
        # For v13, need to force compute
        lines._compute_reconciled_lines()

        for line in lines:
            self.assertEqual(line.reconcile_line_ids, lines)

    def test_02_full_reconcile(self):
        base_move = self.create_account_move(5000, self.account_recv, self.account_sale)

        move2 = self.create_account_move(2500, self.account_sale, self.account_recv)
        move3 = self.create_account_move(2500, self.account_sale, self.account_recv)

        lines = self.AccountMoveLineObj.search(
            [
                ("move_id", "in", [base_move.id, move2.id, move3.id]),
                ("account_id", "=", self.account_recv.id),
            ]
        )
        lines.mapped("move_id").action_post()
        lines.reconcile()
        # For v13, need to force compute
        lines._compute_reconciled_lines()

        for line in lines:
            self.assertEqual(line.reconcile_line_ids, lines)
            self.assertEqual(
                line.full_reconcile_id.reconciled_line_ids, line.reconcile_line_ids
            )
