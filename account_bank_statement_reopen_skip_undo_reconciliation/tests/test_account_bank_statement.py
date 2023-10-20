# Copyright 2022 ForgeFlow S.L.
# @author Jordi Ballester <jordi.ballester@forgeflow.com.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.test_account_bank_statement import (
    TestAccountBankStatementCommon,
)


@tagged("post_install", "-at_install")
class TestAccountBankStatementLine(TestAccountBankStatementCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )

    def test_button_undo_reconciliation(self):
        statement = self.env["account.bank.statement"].create(
            {
                "name": "test_statement",
                "date": "2019-01-01",
                "journal_id": self.bank_journal_2.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "date": "2019-01-01",
                            "payment_ref": "line_1",
                            "partner_id": self.partner_a.id,
                            "amount": 1000,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "date": "2019-01-01",
                            "payment_ref": "line_2",
                            "partner_id": self.partner_a.id,
                            "amount": 2000,
                        },
                    ),
                ],
            }
        )
        statement_line = statement.line_ids[0]

        test_invoice = self.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "invoice_date": fields.Date.from_string("2016-01-01"),
                    "date": fields.Date.from_string("2016-01-01"),
                    "partner_id": self.partner_a.id,
                    "invoice_line_ids": [
                        (
                            0,
                            None,
                            {
                                "name": "counterpart line, same amount",
                                "account_id": self.company_data[
                                    "default_account_revenue"
                                ].id,
                                "quantity": 1,
                                "price_unit": 1000,
                            },
                        ),
                    ],
                }
            ]
        )
        test_invoice.action_post()
        statement.button_post()
        counterpart_lines = test_invoice.mapped("line_ids").filtered(
            lambda line: line.account_internal_type in ("receivable", "payable")
        )
        statement_line.reconcile([{"id": counterpart_lines[0].id}])
        self.assertEqual(counterpart_lines.reconciled, True)
        statement.button_reopen()
        self.assertEqual(counterpart_lines.reconciled, True)
        self.assertEqual(statement_line.move_id.state, "posted")
        second_statement_line = statement.line_ids[0]
        self.assertEqual(second_statement_line.move_id.state, "draft")
        statement_line.button_undo_reconciliation()
        self.assertEqual(statement_line.move_id.state, "draft")
