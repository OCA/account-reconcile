# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests import common
import time

ACC_NUMBER = "BE38733040385372"


class test_regex_account_completion(common.TransactionCase):

    def prepare(self):
        self.st_obj = self.registry(
            "account.bank.statement")
        self.st_line_obj = self.registry(
            "account.bank.statement.line")
        self.account_id = self.ref('account.a_expense')
        # create the completion rule
        rule_vals = {'function_to_call': 'set_account',
                     'regex': '^My statement',
                     'account_id': self.account_id}
        completion_rule_id = self.registry(
            "account.statement.completion.rule").create(
            self.cr, self.uid, rule_vals)
        # Create the profile
        journal_id = self.ref("account.bank_journal")
        profile_id = self.registry("account.statement.profile").create(
            self.cr, self.uid, {
                "name": "TEST",
                "commission_account_id": self.ref("account.a_recv"),
                "journal_id": journal_id,
                "rule_ids": [(6, 0, [completion_rule_id])]
            })
        # Create a bank statement
        self.statement_id = self.st_obj.create(
            self.cr, self.uid, {
                "balance_end_real": 0.0,
                "balance_start": 0.0,
                "date": time.strftime('%Y-%m-%d'),
                "journal_id": journal_id,
                "profile_id": profile_id
            })
        # Create two bank statement lines
        self.statement_line1_id = self.st_line_obj.create(self.cr, self.uid, {
            'amount': 1000.0,
            'name': 'My statement',
            'ref': 'My ref',
            'statement_id': self.statement_id,
            'partner_acc_number': ACC_NUMBER
        })

        self.statement_line2_id = self.st_line_obj.create(self.cr, self.uid, {
            'amount': 2000.0,
            'name': 'My second statement',
            'ref': 'My second ref',
            'statement_id': self.statement_id,
            'partner_acc_number': ACC_NUMBER
        })

    def test_00(self):
        """Test the automatic completion on account
        """
        self.prepare()
        statement_obj = self.st_obj.browse(
            self.cr, self.uid, self.statement_id)
        statement_obj.button_auto_completion()
        statement_line1 = self.st_line_obj.browse(
            self.cr, self.uid, self.statement_line1_id)
        self.assertEquals(self.account_id, statement_line1.account_id.id,
                          "The account should be the account of the completion"
                          )
        statement_line2 = self.st_line_obj.browse(
            self.cr, self.uid, self.statement_line2_id)
        self.assertNotEqual(self.account_id, statement_line2.account_id.id,
                            "The account should be not the account of the "
                            "completion")
