# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import odoo.tests
from odoo import fields

from odoo.addons.account.tests.common import TestAccountReconciliationCommon


@odoo.tests.tagged("post_install", "-at_install")
class TestInvoice(TestAccountReconciliationCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.account_move_obj = cls.env["account.move"]
        cls.account_move_line_obj = cls.env["account.move.line"]
        cls.journal = cls.company_data["default_journal_bank"]
        cls.account_id = cls.journal.default_account_id.id

    def test_all_completion_rules(self):
        # I fill in the field Bank Statement Label in a Partner
        self.partner_4 = self.env.ref("base.res_partner_4")
        self.partner_4.bank_statement_label = "XXX66Z"
        self.assertEqual(self.partner_4.bank_statement_label, "XXX66Z")

        self.invoice_for_completion_1 = self._create_invoice(
            date_invoice=fields.Date.today(), auto_validate=True
        )
        self.assertEqual(self.invoice_for_completion_1.state, "posted")
        self.assertEqual(
            self.invoice_for_completion_1.name,
            fields.Date.today().strftime("INV/%Y/%m/0001"),
        )

        self.demo_invoice_0 = self._create_invoice(
            move_type="in_invoice", auto_validate=True
        )
        self.demo_invoice_0.ref = "T2S12345"

        self.refund_for_completion_1 = self._create_invoice(
            move_type="out_refund", date_invoice=fields.Date.today(), auto_validate=True
        )
        self.assertEqual(
            self.refund_for_completion_1.name,
            fields.Date.today().strftime("RINV/%Y/%m/0001"),
        )

        # In order to test the banking framework, I first need to create a
        # journal
        completion_rule_4 = self.env.ref(
            "account_move_base_import.bank_statement_completion_rule_4"
        )
        completion_rule_2 = self.env.ref(
            "account_move_base_import.bank_statement_completion_rule_2"
        )
        completion_rule_3 = self.env.ref(
            "account_move_base_import.bank_statement_completion_rule_3"
        )
        completion_rule_5 = self.env.ref(
            "account_move_base_import.bank_statement_completion_rule_5"
        )
        completion_rules = (
            completion_rule_2
            | completion_rule_3
            | completion_rule_4
            | completion_rule_5
        )
        self.journal.write(
            {
                "used_for_completion": True,
                "rule_ids": [
                    (4, comp_rule.id, False) for comp_rule in completion_rules
                ],
            }
        )
        # Now I create a statement. I create statment lines separately because
        # I need to find each one by XML id
        move_test1 = (
            self.env["account.move"]
            .with_context(check_move_validity=False)
            .create({"name": "Move 2", "journal_id": self.journal.id})
        )
        # I create a move line for a CI
        move_line_ci = (
            self.env["account.move.line"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "name": "\\",
                    "account_id": self.company_data["default_account_receivable"].id,
                    "move_id": move_test1.id,
                    "date_maturity": fields.Date.from_string("2013-12-20"),
                    "credit": 0.0,
                }
            )
        )
        # I create a move line for a SI
        move_line_si = (
            self.env["account.move.line"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "name": "\\",
                    "account_id": self.company_data["default_account_expense"].id,
                    "move_id": move_test1.id,
                    "date_maturity": fields.Date.from_string("2013-12-19"),
                    "debit": 0.0,
                }
            )
        )
        # I create a move line for a CR
        move_line_cr = (
            self.env["account.move.line"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "name": "\\",
                    "account_id": self.company_data["default_account_expense"].id,
                    "move_id": move_test1.id,
                    "date_maturity": fields.Date.from_string("2013-12-19"),
                    "debit": 0.0,
                }
            )
        )
        # I create a move line for the Partner Name
        move_line_partner_name = (
            self.env["account.move.line"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "name": "Test autocompletion based on Partner Name Deco Addict",
                    "account_id": self.company_data["default_account_receivable"].id,
                    "move_id": move_test1.id,
                    "date_maturity": fields.Date.from_string("2013-12-17"),
                    "credit": 0.0,
                }
            )
        )
        # I create a move line for the Partner Label
        move_line_partner_label = (
            self.env["account.move.line"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "name": "XXX66Z",
                    "account_id": self.company_data["default_account_receivable"].id,
                    "move_id": move_test1.id,
                    "date_maturity": "2013-12-24",
                    "debit": 0.0,
                }
            )
        )
        # and add the correct name
        move_line_ci.with_context(check_move_validity=False).write(
            {"name": fields.Date.today().strftime("INV/%Y/%m/0001"), "credit": 210.0}
        )
        move_line_si.with_context(check_move_validity=False).write(
            {"name": "T2S12345", "debit": 65.0}
        )
        move_line_cr.with_context(check_move_validity=False).write(
            {"name": fields.Date.today().strftime("RINV/%Y/%m/0001"), "debit": 210.0}
        )
        move_line_partner_name.with_context(check_move_validity=False).write(
            {"credit": 600.0}
        )
        move_line_partner_label.with_context(check_move_validity=False).write(
            {"debit": 932.4}
        )
        # I run the auto complete
        move_test1.button_auto_completion()
        # Now I can check that all is nice and shiny, line 1. I expect the
        # Customer Invoice Number to be recognised.
        # I Use _ref, because ref conflicts with the field ref of the
        # statement line
        self.assertEqual(
            move_line_ci.partner_id.id,
            self.partner_agrolait_id,
            msg="Check completion by CI number",
        )
        # Line 2. I expect the Supplier invoice number to be recognised. The
        # supplier invoice was created by the account module demo data, and we
        # confirmed it here.
        self.assertEqual(
            move_line_si.partner_id.id,
            self.partner_agrolait_id,
            msg="Check completion by SI number",
        )
        # Line 3. I expect the Customer refund number to be recognised. It
        # should be the commercial partner, and not the regular partner.
        self.assertEqual(
            move_line_cr.partner_id.id,
            self.partner_agrolait_id,
            msg="Check completion by CR number and commercial partner",
        )
        # Line 4. I check that the partner name has been recognised.
        self.assertEqual(
            move_line_partner_name.partner_id.name,
            "Deco Addict",
            msg="Check completion by partner name",
        )
        # Line 5. I check that the partner special label has been recognised.
        self.partner_4 = self.env.ref("base.res_partner_4")
        self.assertEqual(
            move_line_partner_label.partner_id,
            self.partner_4,
            msg="Check completion by partner label",
        )
