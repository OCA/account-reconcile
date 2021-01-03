# Copyright 2011-2016 Akretion
# Copyright 2011-2019 Camptocamp SA
# Copyright 2013 Savoir-faire Linux
# Copyright 2014 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from collections import namedtuple

import odoo.tests
from odoo import fields

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

name_completion_case = namedtuple(
    "name_completion_case", ["partner_name", "line_label", "should_match"]
)
NAMES_COMPLETION_CASES = [
    name_completion_case("Acsone", "Line for Acsone SA", True),
    name_completion_case("Acsone", "Line for Acsone", True),
    name_completion_case("Acsone", "Acsone for line", True),
    name_completion_case("acsone", "Acsone for line", True),
    name_completion_case("Acsone SA", "Line for Acsone SA test", True),
    name_completion_case("Ac..ne", "Acsone for line", False),
    name_completion_case("é@|r{}", "Acsone é@|r{} for line", True),
    name_completion_case("Acsone", "A..one for line", False),
    name_completion_case("A.one SA", "A.one SA for line", True),
    name_completion_case(
        "Acsone SA", "Line for Acsone ([^a-zA-Z0-9 -]) SA test", False
    ),
    name_completion_case(
        "Acsone ([^a-zA-Z0-9 -]) SA",
        "Line for Acsone ([^a-zA-Z0-9 -]) SA " "test",
        True,
    ),
    name_completion_case(
        r"Acsone (.^$*+?()[{\| -]\) SA",
        r"Line for Acsone (.^$*+?()[{\| -]\) " r"SA test",
        True,
    ),
    name_completion_case("Acšone SA", "Line for Acšone SA test", True),
]


@odoo.tests.tagged("post_install", "-at_install")
class BaseCompletion(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.account_move_obj = cls.env["account.move"]
        cls.account_move_line_obj = cls.env["account.move.line"]
        cls.journal = cls.company_data["default_journal_bank"]
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.account_id = cls.journal.default_account_id.id

    def test_name_completion(self):
        """Test complete partner_id from statement line label
        Test the automatic completion of the partner_id based if the name of
        the partner appears in the statement line label
        """
        self.completion_rule_id = self.ref(
            "account_move_base_import.bank_statement_completion_rule_3"
        )
        # Create the profile
        self.journal.write(
            {
                "used_for_completion": True,
                "rule_ids": [(6, 0, [self.completion_rule_id])],
            }
        )
        # Create an account move
        self.move = self.account_move_obj.create(
            {"date": fields.Date.today(), "journal_id": self.journal.id}
        )

        for case in NAMES_COMPLETION_CASES:
            self.partner.write({"name": case.partner_name})
            self.move_line = self.account_move_line_obj.with_context(
                check_move_validity=False
            ).create(
                {
                    "account_id": self.account_id,
                    "credit": 1000.0,
                    "name": case.line_label,
                    "move_id": self.move.id,
                }
            )
            self.assertFalse(
                self.move_line.partner_id, "Partner_id must be blank before completion"
            )
            self.move.with_context(check_move_validity=False).button_auto_completion()
            if case.should_match:
                self.assertEqual(
                    self.partner,
                    self.move_line.partner_id,
                    "Missing expected partner id after completion "
                    "(partner_name: %s, line_name: %s)"
                    % (case.partner_name, case.line_label),
                )
            else:
                self.assertNotEqual(
                    self.partner,
                    self.move_line.partner_id,
                    "Partner id should be empty after completion "
                    "(partner_name: %s, line_name: %s)"
                    % (case.partner_name, case.line_label),
                )
