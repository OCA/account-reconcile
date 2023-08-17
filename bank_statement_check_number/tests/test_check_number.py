from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestCheckNumber(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.bank_journal = cls.company_data["default_journal_bank"]
        cls.currency = cls.currency_data["currency"]
        cls.statement = cls.env["account.bank.statement"].create(
            {
                "name": "test_statement",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "date": "2019-01-01",
                            "payment_ref": "line_1",
                            "partner_id": cls.partner_a.id,
                            "foreign_currency_id": cls.currency.id,
                            "journal_id": cls.bank_journal.id,
                            "amount": 1250.0,
                            "amount_currency": 2500.0,
                            "check_number": "111",
                        },
                    ),
                ],
            }
        )
        cls.statement_line = cls.statement.line_ids

    def test_01_check_number(self):

        self.assertEqual(self.statement_line.check_number, "111")
