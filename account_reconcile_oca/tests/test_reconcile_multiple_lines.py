# Copyright 2025 Simone Rubino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form, tagged

from odoo.addons.account_reconcile_model_oca.tests.common import (
    TestAccountReconciliationCommon,
)


@tagged("post_install", "-at_install")
class TestReconcileMultipleLines(TestAccountReconciliationCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        (cls.reconcile_account,) = cls.env["account.account"].create(
            [
                {
                    "name": "Test account for reconciliation",
                    "code": "TSTREC",
                    "account_type": "liability_payable",
                }
            ]
        )

        cls.bank_journal = cls.company_data["default_journal_bank"]
        (
            cls.bank_line_1,
            cls.bank_line_2,
        ) = cls.env["account.bank.statement.line"].create(
            [
                {
                    "journal_id": cls.bank_journal.id,
                    "date": "2020-01-01",
                    "amount": 100,
                },
                {
                    "journal_id": cls.bank_journal.id,
                    "date": "2020-01-01",
                    "amount": 600,
                },
            ],
        )
        (cls.reconcile_model,) = cls.env["account.reconcile.model"].create(
            [
                {
                    "name": "Test Writeoff",
                    "rule_type": "writeoff_button",
                    "line_ids": [
                        Command.create(
                            {
                                "account_id": cls.reconcile_account.id,
                            }
                        ),
                    ],
                },
            ]
        )

    def _get_wizard(self, statement_lines, reconcile_model):
        selection_context = {
            "active_model": statement_lines._name,
            "active_ids": statement_lines.ids,
        }
        wizard_model = self.env[
            "account_reconcile_oca.reconcile_multiple_lines"
        ].with_context(**selection_context)
        wizard_form = Form(wizard_model)
        wizard_form.manual_model_id = reconcile_model
        return wizard_form.save()

    def test_writeoff_2_lines(self):
        """The wizard can writeoff 2 statement lines."""
        # Arrange
        reconcile_account = self.reconcile_account
        statement_lines = self.bank_line_1 | self.bank_line_2
        writeoff_reconcile_model = self.reconcile_model
        wizard = self._get_wizard(statement_lines, writeoff_reconcile_model)
        # pre-condition
        self.assertEqual(writeoff_reconcile_model.rule_type, "writeoff_button")
        self.assertNotIn(reconcile_account, statement_lines.line_ids.account_id)

        # Act
        wizard.run()

        # Assert
        self.assertIn(reconcile_account, statement_lines.line_ids.account_id)
