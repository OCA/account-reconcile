# Copyright 2024 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountBankStatementLineCreation(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.bank_journal_1 = cls.company_data["default_journal_bank"]
        cls.currency_1 = cls.company_data["currency"]
        cls.statement = cls.env["account.bank.statement"].create(
            {
                "name": "test_statement",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "date": "2024-01-01",
                            "payment_ref": "line_1",
                            "journal_id": cls.bank_journal_1.id,
                            "amount": 1000.0,
                        },
                    ),
                ],
            }
        )
        cls.statement_line = cls.statement.line_ids

    def test_bank_statement_line_creation(self):
        """
        Check that we can create a new statement.
        """
        self.statement.line_ids.new()
        self.statement._compute_date_index()
        self.assertEqual(len(self.statement.line_ids), 2)
