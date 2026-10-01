# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
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
                ("company_ids", "=", cls.company.id),
                ("reconcile", "=", True),
                ("account_type", "=", "asset_receivable"),
            ],
            limit=1,
        )
        cls.other_account = cls.env["account.account"].search(
            [("company_ids", "=", cls.company.id), ("reconcile", "=", False)], limit=1
        )
        cls.journal = cls.env["account.journal"].search(
            [("company_id", "=", cls.company.id), ("type", "=", "general")], limit=1
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Odoo Community Association", "company_id": cls.company.id}
        )
        cls.writeoff_account = cls.env["account.account"].search(
            [
                ("company_ids", "=", cls.company.id),
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

        cls.three_days_ago = fields.Date.today() - timedelta(days=3)
        cls.env["res.currency.rate"].create(
            {
                "currency_id": cls.foreign_curr.id,
                "rate": 0.8,
                "name": cls.three_days_ago,
                "company_id": cls.company.id,
            }
        )
        cls.two_days_ago = fields.Date.today() - timedelta(days=2)
        cls.env["res.currency.rate"].create(
            {
                "currency_id": cls.foreign_curr.id,
                "rate": 0.95,
                "name": cls.two_days_ago,
                "company_id": cls.company.id,
            }
        )
        cls.one_day_ago = fields.Date.today() - timedelta(days=1)
        cls.env["res.currency.rate"].create(
            {
                "currency_id": cls.foreign_curr.id,
                "rate": 1.1,
                "name": cls.one_day_ago,
                "company_id": cls.company.id,
            }
        )

    def _create_rec_line(
        self, amount, currency=None, company_amount=None, move_date=None, side="debit"
    ):
        is_debit = side == "debit"
        date_move = move_date or fields.Date.today()

        rec_line_vals = {
            "name": f"Test {side}",
            "account_id": self.rec_account.id,
            "partner_id": self.partner.id,
        }

        if currency:
            rec_line_vals.update(
                {
                    "currency_id": currency.id,
                    "amount_currency": amount if is_debit else -amount,
                }
            )
            if company_amount is not None:
                # only if we force the rate, could be the case on payment where rate
                # comes from the bank for instance
                rec_line_vals.update(
                    {
                        "debit": company_amount if is_debit else 0.0,
                        "credit": 0.0 if is_debit else company_amount,
                    }
                )
        else:
            rec_line_vals.update(
                {
                    "debit": amount if is_debit else 0.0,
                    "credit": 0.0 if is_debit else amount,
                }
            )

        move = (
            self.env["account.move"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "journal_id": self.journal.id,
                    "date": date_move,
                    "move_type": "entry",
                    "line_ids": [(0, 0, rec_line_vals)],
                }
            )
        )

        main_line = move.line_ids[0]

        self.env["account.move.line"].with_context(check_move_validity=False).create(
            {
                "move_id": move.id,
                "name": "Contrepartie",
                "account_id": self.other_account.id,
                "partner_id": self.partner.id,
                "debit": main_line.credit,
                "credit": main_line.debit,
                "currency_id": main_line.currency_id.id,
                "amount_currency": -main_line.amount_currency,
            }
        )
        move.action_post()
        return main_line

    def _assert_full_reconciled(self, lines, description):
        self.assertTrue(all(li.reconciled for li in lines), description)
        self.assertEqual(len(lines.full_reconcile_id), 1, description)
        self.assertTrue(all(li.full_reconcile_id for li in lines), description)
        for line in lines:
            self.assertEqual(line.amount_residual, 0.0, description)
            self.assertEqual(line.amount_residual_currency, 0.0, description)

    def test_reconcile_manual(self):
        self.line1 = self._create_rec_line(100, side="debit")
        self.line2 = self._create_rec_line(95, side="credit")
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
        self.assertEqual(self.line1.amount_residual, 5.0)
        self.assertTrue(self.line2.reconciled)
        self.assertEqual(self.line1.matching_number, self.line2.matching_number)

        # reconcile with write-off
        lines_to_rec.remove_move_reconcile()
        wiz2 = (
            self.env["account.move.line.reconcile.manual"]
            .with_context(active_model="account.move.line", active_ids=lines_to_rec.ids)
            .create({})
        )
        self.assertEqual(wiz2.writeoff_type, "expense")
        wiz2.go_to_writeoff()
        self.assertEqual(wiz2.state, "writeoff")
        self.assertFalse(self.ccur.compare_amounts(wiz2.writeoff_amount, -5))
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
        self.line1 = self._create_rec_line(
            95, currency=self.foreign_curr, company_amount=100, side="debit"
        )
        self.line2 = self._create_rec_line(
            95, currency=self.foreign_curr, company_amount=101, side="credit"
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
        self._assert_full_reconciled(
            lines_to_rec, "test_foreign_currency_full_reconcile"
        )
        self.assertEqual(len(self.line1.full_reconcile_id.reconciled_line_ids), 3)

    def _test_full_reconcile_scenarios(self, scenarios):
        for scenario, vals_list in scenarios.items():
            lines_to_rec = self.env["account.move.line"]
            for vals in vals_list:
                lines_to_rec |= self._create_rec_line(
                    vals["amount"],
                    currency=vals.get("currency"),
                    company_amount=vals.get("company_amount"),
                    move_date=vals.get("move_date"),
                    side=vals.get("side"),
                )
            wiz = (
                self.env["account.move.line.reconcile.manual"]
                .with_context(
                    active_model="account.move.line", active_ids=lines_to_rec.ids
                )
                .create({})
            )
            if wiz.writeoff_type == "none":
                wiz.full_reconcile()
            else:
                wiz.go_to_writeoff()
                wiz.write(
                    {
                        "writeoff_journal_id": self.journal.id,
                        "writeoff_ref": self.writeoff_ref,
                        "writeoff_account_id": self.writeoff_account.id,
                    }
                )
                wiz.reconcile_with_writeoff()
            self._assert_full_reconciled(lines_to_rec, scenario)

    def test_foreign_currency_reconcile_with_write_off(self):
        scenarios = {
            "1 - Dual Debit Residual (FC & CC)": [
                {
                    "side": "debit",
                    "currency": self.foreign_curr,
                    "amount": 95,
                    "company_amount": 100,
                },
                {
                    "side": "credit",
                    "currency": self.foreign_curr,
                    "amount": 94,
                    "company_amount": 98,
                },
            ],
            "2 - Mixed Residuals: Debit FC / Credit CC": [
                {
                    "side": "debit",
                    "currency": self.foreign_curr,
                    "amount": 95,
                    "company_amount": 100,
                },
                {
                    "side": "credit",
                    "currency": self.foreign_curr,
                    "amount": 94,
                    "company_amount": 102,
                },
            ],
            "3 - Mixed Residuals: Debit FC / Credit CC - 4 lines": [
                {
                    "side": "debit",
                    "currency": self.foreign_curr,
                    "amount": 95,
                    "company_amount": 100,
                },
                {
                    "side": "debit",
                    "currency": self.foreign_curr,
                    "amount": 95,
                    "company_amount": 150,
                },
                {
                    "side": "credit",
                    "currency": self.foreign_curr,
                    "amount": 95,
                    "company_amount": 90,
                },
                {
                    "side": "credit",
                    "currency": self.foreign_curr,
                    "amount": 94,
                    "company_amount": 170,
                },
            ],
            "4 - No CC residual": [
                {
                    "side": "debit",
                    "currency": self.foreign_curr,
                    "amount": 95,
                    "company_amount": 100,
                },
                {
                    "side": "credit",
                    "currency": self.foreign_curr,
                    "amount": 94,
                    "company_amount": 100,
                },
            ],
        }
        self._test_full_reconcile_scenarios(scenarios)

    def test_multi_currency_full_reconcile(self):
        scenarios = {
            "1 - Credit Residual CC": [
                {
                    "side": "debit",
                    "currency": self.foreign_curr,
                    "amount": 100,
                    "company_amount": 65.41,
                    "move_date": self.two_days_ago,
                },
                {"side": "credit", "amount": 30, "move_date": self.two_days_ago},
            ],
            "2 - debit Residual FC": [
                {
                    "side": "debit",
                    "currency": self.foreign_curr,
                    "amount": 100,
                    "company_amount": 65.41,
                    "move_date": self.three_days_ago,
                },
                {"side": "credit", "amount": 90, "move_date": self.two_days_ago},
            ],
            "3 - No CC residual": [
                {
                    "side": "credit",
                    "currency": self.foreign_curr,
                    "amount": 100,
                    "company_amount": 65.41,
                    "move_date": self.three_days_ago,
                },
                {
                    "side": "credit",
                    "currency": self.foreign_curr,
                    "amount": 100,
                    "company_amount": 80.41,
                    "move_date": self.two_days_ago,
                },
                {"side": "debit", "amount": 60, "move_date": self.two_days_ago},
                {"side": "debit", "amount": 85.82, "move_date": self.one_day_ago},
            ],
        }
        self._test_full_reconcile_scenarios(scenarios)
