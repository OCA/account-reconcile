# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestReconcileManual(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.ref("base.main_company")
        cls.ccur = cls.company.currency_id
        cls.rec_account = cls.env["account.account"].search(
            [("company_id", "=", cls.company.id), ("reconcile", "=", True)], limit=1
        )
        cls.other_account = cls.env["account.account"].search(
            [("company_id", "=", cls.company.id), ("reconcile", "=", False)], limit=1
        )
        cls.journal = cls.env["account.journal"].search(
            [("company_id", "=", cls.company.id), ("type", "=", "general")], limit=1
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Odoo Community Association", "company_id": cls.company.id}
        )
        cls.move1 = cls.env["account.move"].create(
            {
                "journal_id": cls.journal.id,
                "company_id": cls.company.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": cls.rec_account.id,
                            "partner_id": cls.partner.id,
                            "debit": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": cls.other_account.id,
                            "partner_id": cls.partner.id,
                            "credit": 100,
                        },
                    ),
                ],
            }
        )
        cls.move1._post(soft=False)
        cls.line1 = cls.move1.line_ids.filtered(
            lambda x: x.account_id == cls.rec_account
        )
        cls.move2 = cls.env["account.move"].create(
            {
                "journal_id": cls.journal.id,
                "company_id": cls.company.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": cls.rec_account.id,
                            "partner_id": cls.partner.id,
                            "credit": 95,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": cls.other_account.id,
                            "partner_id": cls.partner.id,
                            "debit": 95,
                        },
                    ),
                ],
            }
        )
        cls.move2._post(soft=False)
        cls.line2 = cls.move2.line_ids.filtered(
            lambda x: x.account_id == cls.rec_account
        )
        cls.writeoff_account = cls.env["account.account"].search(
            [
                ("company_id", "=", cls.company.id),
                ("reconcile", "=", False),
                ("account_type", "=", "expense"),
            ],
            limit=1,
        )
        cls.writeoff_ref = "OCApower"

    def test_reconcile_manual(self):
        # start with partial reconcile
        lines_to_rec = self.line1 + self.line2
        wiz1 = (
            self.env["account.move.line.reconcile.manual"]
            .with_context(active_model="account.move.line", active_ids=lines_to_rec.ids)
            .create({})
        )
        self.assertEqual(wiz1.account_id, self.rec_account)
        self.assertEqual(wiz1.company_id, self.company)
        self.assertEqual(wiz1.count, 2)
        self.assertEqual(wiz1.partner_count, 1)
        self.assertEqual(wiz1.partner_id, self.partner)
        self.assertFalse(self.ccur.compare_amounts(wiz1.total_debit, 100))
        self.assertFalse(self.ccur.compare_amounts(wiz1.total_credit, 95))
        self.assertEqual(wiz1.writeoff_type, "expense")
        wiz1.partial_reconcile()

        # reconcile with write-off
        wiz2 = (
            self.env["account.move.line.reconcile.manual"]
            .with_context(active_model="account.move.line", active_ids=lines_to_rec.ids)
            .create({})
        )
        self.assertEqual(wiz2.writeoff_type, "expense")
        wiz2.go_to_writeoff()
        self.assertEqual(wiz2.state, "writeoff")
        self.assertFalse(self.ccur.compare_amounts(wiz2.writeoff_amount, 5))
        wiz2.write(
            {
                "writeoff_journal_id": self.journal.id,
                "writeoff_ref": self.writeoff_ref,
                "writeoff_account_id": self.writeoff_account.id,
            }
        )
        action2 = wiz2.reconcile_with_writeoff()
        self.assertEqual(action2.get("type"), "ir.actions.client")
        wo_move = self.env["account.move"].search(
            [("company_id", "=", self.company.id)], order="id desc", limit=1
        )
        self.assertEqual(wo_move.ref, self.writeoff_ref)
        self.assertEqual(wo_move.journal_id, self.journal)
        self.assertEqual(wo_move.state, "posted")
        self.assertEqual(wo_move.company_id, self.company)
        wo_line = wo_move.line_ids.filtered(lambda x: x.account_id == self.rec_account)
        full_rec2 = wo_line.full_reconcile_id
        self.assertTrue(full_rec2)
        self.assertEqual(self.line1.full_reconcile_id, full_rec2)
        self.assertEqual(self.line2.full_reconcile_id, full_rec2)

        # Cannot start wizard on lines fully reconciled!
        lines_to_rec += wo_line
        with self.assertRaises(UserError):
            self.env["account.move.line.reconcile.manual"].with_context(
                active_model="account.move.line", active_ids=lines_to_rec.ids
            ).create({})

        # Full reconcile
        lines_to_rec.remove_move_reconcile()
        wiz4 = (
            self.env["account.move.line.reconcile.manual"]
            .with_context(active_model="account.move.line", active_ids=lines_to_rec.ids)
            .create({})
        )
        self.assertEqual(wiz4.writeoff_type, "none")
        self.assertFalse(self.ccur.compare_amounts(wiz4.total_debit, 100))
        self.assertFalse(self.ccur.compare_amounts(wiz4.total_credit, 100))
        action4 = wiz4.full_reconcile()
        self.assertEqual(action4.get("type"), "ir.actions.client")
        full_rec4 = wo_line.full_reconcile_id
        self.assertTrue(full_rec4)
        self.assertEqual(self.line1.full_reconcile_id, full_rec4)
        self.assertEqual(self.line2.full_reconcile_id, full_rec4)
