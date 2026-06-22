# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import time

from odoo.tests import Form, tagged

from odoo.addons.account_reconcile_oca.tests.test_bank_account_reconcile import (
    TestAccountReconciliationCommon,
)


@tagged("post_install", "-at_install")
class TestAccountReconcileOcaDueDate(TestAccountReconciliationCommon):
    def test_due_date(self):
        inv1 = self.create_invoice(currency_id=self.currency_usd_id, invoice_amount=100)
        bank_stmt = self.acc_bank_stmt_model.create(
            {
                "journal_id": self.bank_journal_usd.id,
                "date": time.strftime("%Y-07-25"),
                "name": "test",
            }
        )
        bank_stmt_line = self.acc_bank_stmt_line_model.create(
            {
                "name": "testLine",
                "journal_id": self.bank_journal_usd.id,
                "statement_id": bank_stmt.id,
                "amount": 100,
                "date": time.strftime("%Y-07-26"),
                "date_due": time.strftime("%Y-07-30"),
            }
        )
        receivable1 = inv1.line_ids.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        )
        with Form(
            bank_stmt_line,
            view="account_reconcile_oca.bank_statement_line_form_reconcile_view",
        ) as f:
            self.assertFalse(f.can_reconcile)
            f.add_account_move_line_id = receivable1
        self.assertNotEqual(
            bank_stmt_line.date_due, bank_stmt_line.line_ids[0].date_maturity
        )
        self.assertNotEqual(
            bank_stmt_line.date_due, bank_stmt_line.line_ids[1].date_maturity
        )
        self.assertFalse(bank_stmt_line.is_reconciled)
        bank_stmt_line.reconcile_bank_line()
        self.assertTrue(bank_stmt_line.is_reconciled)
        self.assertEqual(
            bank_stmt_line.date_due, bank_stmt_line.line_ids[0].date_maturity
        )
        self.assertEqual(
            bank_stmt_line.date_due, bank_stmt_line.line_ids[1].date_maturity
        )
