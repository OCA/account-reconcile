import time
from odoo.tests import tagged
from odoo.addons.account.tests.common import TestAccountReconciliationCommon
from odoo import Command
from odoo.exceptions import ValidationError


@tagged("post_install", "-at_install")
class TestBankStatement(TestAccountReconciliationCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        # Set the chart_template_ref to the generic COA if not provided
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.acc_bank_stmt_model = cls.env["account.bank.statement"]
        cls.acc_bank_stmt_line_model = cls.env["account.bank.statement.line"]

        cls.bank_stmt1 = cls.acc_bank_stmt_model.create(
            {
                "name": "Statment 1",
                "company_id": cls.env.ref("base.main_company").id,
                "journal_id": cls.bank_journal_euro.id,
                "date": time.strftime("%Y-07-15"),
            })

        cls.bank_stmt2 = cls.acc_bank_stmt_model.create(
            {
                "name": "Statment 2",
                "company_id": cls.env.ref("base.main_company").id,
                "journal_id": cls.bank_journal_euro.id,
                "date": time.strftime("%Y-07-16"),


            })

        cls.bank_stmt_line1 = cls.acc_bank_stmt_line_model.create(
            {
                "name": "Test Line  1",
                "journal_id": cls.bank_journal_euro.id,
                "statement_id": cls.bank_stmt1.id,
                "amount": 150,
                "date": time.strftime("%Y-07-15")
             })
        cls.bank_stmt_line2 = cls.acc_bank_stmt_line_model.create(
            {
                "name": "Test Line  2",
                "journal_id": cls.bank_journal_euro.id,
                "statement_id": cls.bank_stmt1.id,
                "amount": 50,
                "date": time.strftime("%Y-07-15")
             })

        cls.bank_stmt_line3 = cls.acc_bank_stmt_line_model.create(
            {
                 "name": "Test Line  3",
                 "journal_id": cls.bank_journal_euro.id,
                 "statement_id": cls.bank_stmt2.id,
                 "amount": 350,
                 "date": time.strftime("%Y-07-15")
            })


    def test_not_confirm_statement_if_not_valid(self):
        self.bank_stmt1.balance_end_real = 200
        self.bank_stmt2.balance_start = 200
        with self.assertRaises(ValidationError):
            self.bank_stmt2.action_confirm_statement()


