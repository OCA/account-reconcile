# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.tests.common import Form, TransactionCase


class TestAccountReconciliationWidgetDueDate(TransactionCase):
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
        cls.company = cls.env.ref("base.main_company")
        cls.journal = cls.env["account.journal"].create(
            {"name": "Test journal bank", "type": "bank", "code": "BANK-TEST"}
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Account Receivable",
                "code": "AR",
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        cls.partner_a = cls.env["res.partner"].create(
            {
                "name": "Partner Test A",
                "property_account_receivable_id": cls.account.id,
            }
        )
        cls.partner_b = cls.partner_a.copy({"name": "Partner Test B"})
        cls.partner_c = cls.partner_a.copy({"name": "Partner Test C"})
        cls.statement = cls._create_account_bank_statement()

    @classmethod
    def _create_account_bank_statement(cls):
        statement_form = Form(cls.env["account.bank.statement"])
        statement_form.journal_id = cls.journal
        statement_form.date = date(2021, 3, 1)
        statement_form.balance_end_real = 600.00
        with statement_form.line_ids.new() as line_form:
            line_form.date = "2021-01-01"
            line_form.payment_ref = "LINE_A"
            line_form.partner_id = cls.partner_a
            line_form.amount = 100.00
        with statement_form.line_ids.new() as line_form:
            line_form.date = "2021-02-01"
            line_form.date_due = "2021-02-05"
            line_form.payment_ref = "LINE_B"
            line_form.partner_id = cls.partner_b
            line_form.amount = 200.00
        with statement_form.line_ids.new() as line_form:
            line_form.date = "2021-03-01"
            line_form.payment_ref = "LINE_C"
            line_form.partner_id = cls.partner_c
            line_form.amount = 300.00
        return statement_form.save()

    def test_account_reconciliation_widget(self):
        self.assertEqual(self.statement.state, "open")
        self.statement.button_post()
        self.assertEqual(self.statement.state, "posted")
        self.assertEqual(len(self.statement.line_ids), 3)
        reconciliation_widget = self.env["account.reconciliation.widget"]
        account_move_model = self.env["account.move"]
        # line_a
        line_a = self.statement.line_ids.filtered(
            lambda x: x.partner_id == self.partner_a
        )
        self.assertFalse(line_a.date_due, False)
        new_aml_dicts = [
            {
                "account_id": self.partner_a.property_account_receivable_id.id,
                "name": line_a.name,
                "credit": line_a.amount,
            }
        ]
        res = reconciliation_widget.process_bank_statement_line(
            line_a.id,
            [{"partner_id": line_a.partner_id.id, "new_aml_dicts": new_aml_dicts}],
        )
        self.assertEqual(len(res["moves"]), 1)
        move = account_move_model.browse(res["moves"][0])
        self.assertEqual(move.line_ids, line_a.line_ids)
        move_line_credit = move.line_ids.filtered(lambda x: x.debit > 0)
        self.assertFalse(move_line_credit.date_maturity)
        self.assertEqual(move_line_credit.partner_id, self.partner_a)
        # Check that the date_maturity does not change
        move_line_credit.date_maturity = date(2021, 2, 5)
        reconciliation_widget.update_bank_statement_line_due_date(
            res["moves"],
            [line_a.id],
            [line_a.date_due],
        )
        self.assertEqual(move_line_credit.date_maturity, date(2021, 2, 5))
        # line_b
        line_b = self.statement.line_ids.filtered(
            lambda x: x.partner_id == self.partner_b
        )
        self.assertEqual(line_b.date_due, date(2021, 2, 5))
        new_aml_dicts = [
            {
                "account_id": self.partner_b.property_account_receivable_id.id,
                "name": line_b.name,
                "credit": line_b.amount,
            }
        ]
        res = reconciliation_widget.process_bank_statement_line(
            [line_b.id],
            [{"partner_id": line_b.partner_id.id, "new_aml_dicts": new_aml_dicts}],
        )
        reconciliation_widget.update_bank_statement_line_due_date(
            res["moves"],
            [line_b.id],
            [line_b.date_due],
        )
        self.assertEqual(len(res["moves"]), 1)
        move = account_move_model.browse(res["moves"][0])
        self.assertEqual(move.line_ids, line_b.line_ids)
        move_line_credit = move.line_ids.filtered(lambda x: x.debit > 0)
        self.assertEqual(move_line_credit.date_maturity, date(2021, 2, 5))
        self.assertEqual(move_line_credit.partner_id, self.partner_b)
        # line_c
        line_c = self.statement.line_ids.filtered(
            lambda x: x.partner_id == self.partner_c
        )
        self.assertFalse(line_c.date_due)
        new_aml_dicts = [
            {
                "account_id": self.partner_c.property_account_receivable_id.id,
                "name": line_c.name,
                "credit": line_c.amount,
            }
        ]
        res = reconciliation_widget.process_bank_statement_line(
            [line_c.id],
            [{"partner_id": line_c.partner_id.id, "new_aml_dicts": new_aml_dicts}],
        )
        reconciliation_widget.update_bank_statement_line_due_date(
            res["moves"],
            [line_c.id],
            ["2021-02-05"],
        )
        self.assertEqual(line_c.date_due, date(2021, 2, 5))
        self.assertEqual(len(res["moves"]), 1)
        move = account_move_model.browse(res["moves"][0])
        self.assertEqual(move.line_ids, line_c.line_ids)
        move_line_credit = move.line_ids.filtered(lambda x: x.debit > 0)
        self.assertEqual(move_line_credit.date_maturity, date(2021, 2, 5))
        self.assertEqual(move_line_credit.partner_id, self.partner_c)
        # Confirm statement
        self.statement.button_validate_or_action()
        self.assertEqual(self.statement.state, "confirm")
