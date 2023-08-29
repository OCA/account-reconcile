from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestCheckNumber(TransactionCase):
    def setUp(self):
        super().setUp()
        self.journal = self.env["account.journal"].create(
            {
                "name": "Bank2",
                "code": "BNK2",
                "active": True,
                "type": "bank",
            }
        )
        self.partner = self.env["res.partner"].create({"name": "TestPartner"})

        self.date = "2023-08-29"

    def test_01_check_number(self):
        with Form(self.env["account.bank.statement"]) as bank_statement_form:
            bank_statement_form.name = "BankStatementTest"
            bank_statement_form.journal_id = self.journal
            bank_statement_form.date = self.date
            bank_statement_form.balance_start = 1000
            bank_statement_form.balance_end_real = 1000
            with bank_statement_form.line_ids.new() as statement_line:
                statement_line.date = self.date
                statement_line.check_number = "111"
                statement_line.partner_id = self.partner
                statement_line.amount = 1000
                statement_line.payment_ref = "S001"
            statement = bank_statement_form.save()
        statement.button_post()

        self.assertEqual(statement.line_ids.check_number, "111")
