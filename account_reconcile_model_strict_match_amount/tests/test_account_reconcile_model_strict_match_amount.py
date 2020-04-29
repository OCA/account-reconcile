# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.addons.account.tests.test_reconciliation_matching_rules import (
    TestReconciliationMatchingRules,
)


class TestAccountReconcileModelStrictMatchAmount(TestReconciliationMatchingRules):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_3 = cls.env["res.partner"].create({"name": "partner_3"})
        cls.partner_4 = cls.env["res.partner"].create({"name": "partner_4"})
        cls.partner_5 = cls.env["res.partner"].create({"name": "partner_5"})
        cls.partner_6 = cls.env["res.partner"].create({"name": "partner_6"})
        cls.invoice_line_5 = cls._create_invoice_line(150, cls.partner_3, "out_invoice")
        cls.invoice_line_5.ref = "ABC001XYZ"
        cls.invoice_line_6 = cls._create_invoice_line(300, cls.partner_4, "out_invoice")
        cls.invoice_line_6.name = "ABC002XYZ"
        cls.invoice_line_7 = cls._create_invoice_line(450, cls.partner_5, "out_invoice")
        cls.invoice_line_7.move_id.ref = "ABC003XYZ"
        cls.invoice_line_8 = cls._create_invoice_line(600, cls.partner_6, "out_invoice")
        cls.invoice_line_8.move_id.invoice_payment_ref = "ABC004XYZ"
        cls.bank_st_2 = cls.env["account.bank.statement"].create(
            {
                "name": "test bank journal 2",
                "journal_id": cls.company_data["default_journal_bank"].id,
            }
        )

        cls.bank_line_3 = cls.env["account.bank.statement.line"].create(
            {
                "statement_id": cls.bank_st_2.id,
                "name": "ABC001XYZ",
                "partner_id": cls.partner_3.id,
                "amount": 135,
                "sequence": 1,
            }
        )
        cls.bank_line_4 = cls.env["account.bank.statement.line"].create(
            {
                "statement_id": cls.bank_st_2.id,
                "name": "ABC002XYZ",
                "partner_id": cls.partner_4.id,
                "amount": 270,
                "sequence": 2,
            }
        )
        cls.bank_line_5 = cls.env["account.bank.statement.line"].create(
            {
                "statement_id": cls.bank_st_2.id,
                "name": "ABC003XYZ",
                "partner_id": cls.partner_5.id,
                "amount": 405,
                "sequence": 3,
            }
        )
        cls.bank_line_6 = cls.env["account.bank.statement.line"].create(
            {
                "statement_id": cls.bank_st_2.id,
                "name": "ABC004XYZ",
                "partner_id": cls.partner_6.id,
                "amount": 540,
                "sequence": 4,
            }
        )

    def test_auto_reconcile_strict_match_100(self):
        my_rule = self.env["account.reconcile.model"].create(
            {
                "name": "Strict Invoice matching amount 100%",
                "rule_type": "invoice_matching",
                "auto_reconcile": True,
                "match_nature": "both",
                "match_same_currency": True,
                "match_total_amount": True,
                "match_total_amount_param": 100.0,
                "strict_match_total_amount": True,
            }
        )
        self._check_statement_matching(
            my_rule,
            {
                self.bank_line_3.id: {"aml_ids": []},
                self.bank_line_4.id: {"aml_ids": []},
                self.bank_line_5.id: {"aml_ids": []},
                self.bank_line_6.id: {"aml_ids": []},
            },
            statements=self.bank_st_2,
        )

    def test_auto_reconcile_strict_match_90(self):
        my_rule = self.env["account.reconcile.model"].create(
            {
                "name": "Strict Invoice matching amount 90%",
                "rule_type": "invoice_matching",
                "auto_reconcile": True,
                "match_nature": "both",
                "match_same_currency": True,
                "match_total_amount": True,
                "match_total_amount_param": 90.0,
                "strict_match_total_amount": True,
            }
        )
        self._check_statement_matching(
            my_rule,
            {
                self.bank_line_3.id: {
                    "aml_ids": [self.invoice_line_5.id],
                    "model": my_rule,
                    "status": "reconciled",
                },
                self.bank_line_4.id: {
                    "aml_ids": [self.invoice_line_6.id],
                    "model": my_rule,
                    "status": "reconciled",
                },
                self.bank_line_5.id: {
                    "aml_ids": [self.invoice_line_7.id],
                    "model": my_rule,
                    "status": "reconciled",
                },
                self.bank_line_6.id: {
                    "aml_ids": [self.invoice_line_8.id],
                    "model": my_rule,
                    "status": "reconciled",
                },
            },
            statements=self.bank_st_2,
        )
