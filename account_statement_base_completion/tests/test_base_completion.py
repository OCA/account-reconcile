# -*- coding: utf-8 -*-
#
#
# Authors: Laurent Mignon
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
# All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from openerp.tests import common
import time
from collections import namedtuple

name_completion_case = namedtuple(
    "name_completion_case", ["partner_name", "line_label", "should_match"])
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
        "Acsone SA", "Line for Acsone ([^a-zA-Z0-9 -]) SA test", False),
    name_completion_case(
        "Acsone ([^a-zA-Z0-9 -]) SA", "Line for Acsone ([^a-zA-Z0-9 -]) SA "
                                      "test", True),
    name_completion_case(
        r"Acsone (.^$*+?()[{\| -]\) SA", r"Line for Acsone (.^$*+?()[{\| -]\) "
                                         r"SA test", True),
    name_completion_case("Acšone SA", "Line for Acšone SA test", True),
]


class base_completion(common.TransactionCase):

    def setUp(self):
        super(base_completion, self).setUp()
        self.company_a = self.browse_ref('base.main_company')
        self.profile_obj = self.registry("account.statement.profile")
        self.partner_obj = self.registry("res.partner")
        self.account_bank_statement_obj = self.registry(
            "account.bank.statement")
        self.account_bank_statement_line_obj = self.registry(
            "account.bank.statement.line")
        self.journal_id = self.ref("account.bank_journal")
        self.partner_id = self.ref('base.main_partner')
        self.account_id = self.ref("account.a_recv")
        self.partner_id = self.ref("base.res_partner_12")

    def test_name_completion(self):
        """Test complete partner_id from statement line label
        Test the automatic completion of the partner_id based if the name of
        the partner appears in the statement line label
        """
        self.completion_rule_id = self.ref(
            'account_statement_base_completion.'
            'bank_statement_completion_rule_3')
        # Create the profile
        self.profile_id = self.profile_obj.create(self.cr, self.uid, {
            "name": "TEST",
            "commission_account_id": self.account_id,
            "journal_id": self.journal_id,
            "rule_ids": [(6, 0, [self.completion_rule_id])]})
        # Create a bank statement
        self.statement_id = self.account_bank_statement_obj.create(
            self.cr, self.uid, {
                "balance_end_real": 0.0,
                "balance_start": 0.0,
                "date": time.strftime('%Y-%m-%d'),
                "journal_id": self.journal_id,
                "profile_id": self.profile_id
            })

        for case in NAMES_COMPLETION_CASES:
            self.partner_obj.write(
                self.cr, self.uid, self.partner_id, {'name': case.partner_name}
            )
            statement_line_id = self.account_bank_statement_line_obj.create(
                self.cr, self.uid, {
                    'amount': 1000.0,
                    'name': case.line_label,
                    'ref': 'My ref',
                    'statement_id': self.statement_id,
                })
            statement_line = self.account_bank_statement_line_obj.browse(
                self.cr, self.uid, statement_line_id)
            self.assertFalse(
                statement_line.partner_id,
                "Partner_id must be blank before completion")
            statement_obj = self.account_bank_statement_obj.browse(
                self.cr, self.uid, self.statement_id)
            statement_obj.button_auto_completion()
            statement_line = self.account_bank_statement_line_obj.browse(
                self.cr, self.uid, statement_line_id)
            if case.should_match:
                self.assertEquals(
                    self.partner_id, statement_line.partner_id['id'],
                    "Missing expected partner id after completion "
                    "(partner_name: %s, line_name: %s)" %
                    (case.partner_name, case.line_label))
            else:
                self.assertNotEquals(
                    self.partner_id, statement_line.partner_id['id'],
                    "Partner id should be empty after completion "
                    "(partner_name: %s, line_name: %s)"
                    % (case.partner_name, case.line_label))
