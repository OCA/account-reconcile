# Copyright 2024-2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import time

from odoo import Command
from odoo.tests import Form, tagged
from odoo.tools import mute_logger

from odoo.addons.account_reconcile_model_oca.tests.common import (
    TestAccountReconciliationCommon,
)


@tagged("post_install", "-at_install")
class TestAccountReconcileAnalyticTag(TestAccountReconciliationCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id += cls.env.ref("analytic.group_analytic_accounting")
        cls.env.user.groups_id += cls.env.ref(
            "account_analytic_tag.group_analytic_tags"
        )
        bank_stmt = cls.env["account.bank.statement"].create(
            {
                "company_id": cls.env.company.id,
                "journal_id": cls.bank_journal_euro.id,
                "date": time.strftime("%Y-07-15"),
                "name": "test",
            }
        )
        cls.bank_stmt_line = cls.env["account.bank.statement.line"].create(
            {
                "name": "testLine",
                "journal_id": cls.bank_journal_euro.id,
                "statement_id": bank_stmt.id,
                "amount": 50,
                "date": time.strftime("%Y-07-15"),
            }
        )
        cls.plan = cls.env["account.analytic.plan"].create({"name": "Test Plan"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test account",
                "plan_id": cls.plan.id,
            },
        )
        cls.analytic_tag = cls.env["account.analytic.tag"].create({"name": "Test tag"})

    @mute_logger("odoo.models.unlink")
    def test_account_reconcile_manual_with_tags(self):
        reconcile_data = self.bank_stmt_line._default_reconcile_data()
        data = reconcile_data["data"][1]
        self.bank_stmt_line.manual_reference = data["reference"]
        self.bank_stmt_line._process_manual_reconcile_from_line(data)
        line_form = Form(
            self.bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        )
        line_form.manual_partner_id = self.partner_a
        line_form.manual_analytic_tag_ids.add(self.analytic_tag)
        line_form.save()
        # The appropriate values are defined in reconcile_data_info (works properly
        # in interface)
        reconcile_data_info = self.bank_stmt_line.reconcile_data_info
        reconcile_data_info["data"][1]["analytic_distribution"] = {
            self.analytic_account.id: 100
        }
        reconcile_data_info["data"][1]["manual_analytic_tag_ids"] = [
            Command.set(self.analytic_tag.ids)
        ]
        self.bank_stmt_line.reconcile_data_info = reconcile_data_info
        self.bank_stmt_line.reconcile_bank_line()
        analytic_line = self.bank_stmt_line.move_id.line_ids.analytic_line_ids
        self.assertTrue(analytic_line)
        self.assertEqual(
            analytic_line.tag_ids, self.bank_stmt_line.manual_analytic_tag_ids
        )

    @mute_logger("odoo.models.unlink")
    def test_account_reconcile_manual_without_tags(self):
        reconcile_data = self.bank_stmt_line._default_reconcile_data()
        data = reconcile_data["data"][1]
        self.bank_stmt_line.manual_reference = data["reference"]
        self.bank_stmt_line._process_manual_reconcile_from_line(data)
        line_form = Form(
            self.bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        )
        line_form.manual_partner_id = self.partner_a
        line_form.save()
        # The appropriate values are defined in reconcile_data_info (works properly
        # in interface)
        reconcile_data_info = self.bank_stmt_line.reconcile_data_info
        reconcile_data_info["data"][1]["analytic_distribution"] = {
            self.analytic_account.id: 100
        }
        self.bank_stmt_line.reconcile_data_info = reconcile_data_info
        self.bank_stmt_line.reconcile_bank_line()
        analytic_line = self.bank_stmt_line.move_id.line_ids.analytic_line_ids
        self.assertTrue(analytic_line)
        self.assertFalse(analytic_line.tag_ids)
