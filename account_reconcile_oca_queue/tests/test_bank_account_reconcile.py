# Copyright 2025 Jacques-Etienne Baudoux (BICM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import time

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account_reconcile_oca.tests.test_bank_account_reconcile import (
    TestAccountReconciliationCommon,
)
from odoo.addons.queue_job.tests.common import trap_jobs


@tagged("post_install", "-at_install")
class TestReconciliationAuto(TestAccountReconciliationCommon):
    def test_reconcile_rule_on_create(self):
        """
        Testing the fill of the bank statment line with
        writeoff suggestion reconcile model with auto_reconcile
        """
        self.env["account.reconcile.model"].create(
            {
                "name": "write-off model suggestion",
                "rule_type": "writeoff_suggestion",
                "match_label": "contains",
                "match_label_param": "DEMO WRITEOFF",
                "auto_reconcile": True,
                "line_ids": [
                    Command.create({"account_id": self.current_assets_account.id})
                ],
            }
        )

        self.env.company.account_auto_reconcile_queue = True

        with trap_jobs() as trap:
            bank_stmt = self.acc_bank_stmt_model.create(
                {
                    "journal_id": self.bank_journal_euro.id,
                    "date": time.strftime("%Y-07-15"),
                    "name": "test",
                }
            )
            bank_stmt_line = self.acc_bank_stmt_line_model.create(
                {
                    "name": "DEMO WRITEOFF",
                    "payment_ref": "DEMO WRITEOFF",
                    "journal_id": self.bank_journal_euro.id,
                    "statement_id": bank_stmt.id,
                    "amount": 100,
                    "date": time.strftime("%Y-07-15"),
                }
            )
            self.assertFalse(bank_stmt_line.is_reconciled)
            trap.assert_jobs_count(1)
            trap.perform_enqueued_jobs()
            self.assertTrue(bank_stmt_line.is_reconciled)
