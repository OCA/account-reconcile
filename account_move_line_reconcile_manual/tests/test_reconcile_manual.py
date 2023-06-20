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
            [
                ("company_id", "=", cls.company.id),
                ("reconcile", "=", True),
                ("account_type", "=", "asset_receivable"),
            ],
            limit=1,
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
        cls.writeoff_account = cls.env["account.account"].search(
            [
                ("company_id", "=", cls.company.id),
                ("reconcile", "=", False),
                ("account_type", "=", "expense"),
            ],
            limit=1,
        )
        cls.writeoff_ref = "OCApower"
        cls.foreign_curr = (
            cls.env["res.currency"]
            .with_context(active_test=False)
            .search([("id", "!=", cls.ccur.id)], limit=1)
        )
        cls.foreign_curr.write({"active": True})

    def _generate_debit_reconcile_move(self, amount, currency_amount=0.0):
        reconcile_line_vals = {
            "account_id": self.rec_account.id,
            "partner_id": self.partner.id,
            "debit": amount,
        }
        other_line_vals = {
            "account_id": self.other_account.id,
            "partner_id": self.partner.id,
            "credit": amount,
        }
        if currency_amount:
            reconcile_line_vals.update(
                {
                    "amount_currency": currency_amount,
                    "currency_id": self.foreign_curr.id,
                }
            )
            other_line_vals.update(
                {
                    "amount_currency": -currency_amount,
                    "currency_id": self.foreign_curr.id,
                }
            )

        move = self.env["account.move"].create(
            {
                "journal_id": self.journal.id,
                "company_id": self.company.id,
                "currency_id": not currency_amount
                and self.ccur.id
                or self.foreign_curr.id,
                "line_ids": [
                    (
                        0,
                        0,
                        reconcile_line_vals,
                    ),
                    (
                        0,
                        0,
                        other_line_vals,
                    ),
                ],
            }
        )
        move._post(soft=False)
        return move

    def _generate_credit_reconcile_move(self, amount, currency_amount=0.0):
        reconcile_line_vals = {
            "account_id": self.rec_account.id,
            "partner_id": self.partner.id,
            "credit": amount,
        }
        other_line_vals = {
            "account_id": self.other_account.id,
            "partner_id": self.partner.id,
            "debit": amount,
        }
        if currency_amount:
            reconcile_line_vals.update(
                {
                    "amount_currency": -currency_amount,
                    "currency_id": self.foreign_curr.id,
                }
            )
            other_line_vals.update(
                {
                    "amount_currency": currency_amount,
                    "currency_id": self.foreign_curr.id,
                }
            )

        move = self.env["account.move"].create(
            {
                "journal_id": self.journal.id,
                "company_id": self.company.id,
                "currency_id": not currency_amount
                and self.ccur.id
                or self.foreign_curr.id,
                "line_ids": [
                    (
                        0,
                        0,
                        reconcile_line_vals,
                    ),
                    (
                        0,
                        0,
                        other_line_vals,
                    ),
                ],
            }
        )
        move._post(soft=False)
        return move

    def test_reconcile_manual(self):
        self.move1 = self._generate_debit_reconcile_move(100)
        self.line1 = self.move1.line_ids.filtered(
            lambda x: x.account_id == self.rec_account
        )
        self.move2 = self._generate_credit_reconcile_move(95)
        self.line2 = self.move2.line_ids.filtered(
            lambda x: x.account_id == self.rec_account
        )
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

    def test_foreign_currency_full_reconcile(self):
        self.move1 = self._generate_debit_reconcile_move(100, currency_amount=95)
        self.line1 = self.move1.line_ids.filtered(
            lambda x: x.account_id == self.rec_account
        )
        self.move2 = self._generate_credit_reconcile_move(101, currency_amount=95)
        self.line2 = self.move2.line_ids.filtered(
            lambda x: x.account_id == self.rec_account
        )
        lines_to_rec = self.line1 + self.line2
        wiz = (
            self.env["account.move.line.reconcile.manual"]
            .with_context(active_model="account.move.line", active_ids=lines_to_rec.ids)
            .create({})
        )
        self.assertEqual(wiz.account_id, self.rec_account)
        self.assertEqual(wiz.count, 2)
        self.assertEqual(wiz.partner_count, 1)
        self.assertFalse(self.foreign_curr.compare_amounts(wiz.total_debit, 95))
        self.assertFalse(self.foreign_curr.compare_amounts(wiz.total_credit, 95))
        self.assertEqual(wiz.writeoff_type, "none")
        wiz.full_reconcile()

        self.assertTrue(self.line1.full_reconcile_id)
        self.assertEqual(self.line1.full_reconcile_id, self.line2.full_reconcile_id)
        self.assertFalse(self.line1.amount_residual_currency)
        self.assertFalse(self.line1.amount_residual)

    def test_foreign_currency_reconcile_with_write_off(self):
        self.move1 = self._generate_debit_reconcile_move(100, currency_amount=95)
        self.line1 = self.move1.line_ids.filtered(
            lambda x: x.account_id == self.rec_account
        )
        self.move2 = self._generate_credit_reconcile_move(98, currency_amount=94)
        self.line2 = self.move2.line_ids.filtered(
            lambda x: x.account_id == self.rec_account
        )
        lines_to_rec = self.line1 + self.line2
        wiz = (
            self.env["account.move.line.reconcile.manual"]
            .with_context(active_model="account.move.line", active_ids=lines_to_rec.ids)
            .create({})
        )
        self.assertEqual(wiz.account_id, self.rec_account)
        self.assertEqual(wiz.count, 2)
        self.assertEqual(wiz.writeoff_type, "expense")
        self.assertEqual(wiz.writeoff_amount, 1)
        wiz.go_to_writeoff()
        wiz.write(
            {
                "writeoff_journal_id": self.journal.id,
                "writeoff_ref": self.writeoff_ref,
                "writeoff_account_id": self.writeoff_account.id,
            }
        )
        wiz.reconcile_with_writeoff()

        self.assertTrue(self.line1.full_reconcile_id)
        self.assertEqual(self.line1.full_reconcile_id, self.line2.full_reconcile_id)

    def test_multi_currency_full_reconcile(self):
        self.move1 = self._generate_debit_reconcile_move(65.41, currency_amount=100)
        self.line1 = self.move1.line_ids.filtered(
            lambda x: x.account_id == self.rec_account
        )
        self.move2 = self._generate_credit_reconcile_move(30)
        self.line2 = self.move2.line_ids.filtered(
            lambda x: x.account_id == self.rec_account
        )
        lines_to_rec = self.line1 + self.line2
        wiz = (
            self.env["account.move.line.reconcile.manual"]
            .with_context(active_model="account.move.line", active_ids=lines_to_rec.ids)
            .create({})
        )
        self.assertEqual(wiz.writeoff_type, "expense")
        wiz.go_to_writeoff()
        wiz.write(
            {
                "writeoff_journal_id": self.journal.id,
                "writeoff_ref": self.writeoff_ref,
                "writeoff_account_id": self.writeoff_account.id,
            }
        )
        wiz.reconcile_with_writeoff()
