# -*- coding: utf-8 -*-
#
#
# Authors: Laurent Mignon
# Copyright (c) 2013 Acsone SA/NV (http://www.acsone.eu)
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

ACC_NUMBER = "BE38733040385372"


class bankaccount_completion(common.TransactionCase):

    def prepare(self):
        self.company_a = self.browse_ref('base.main_company')
        self.profile_obj = self.registry("account.statement.profile")
        self.account_bank_statement_obj = self.registry("account.bank.statement")
        self.account_bank_statement_line_obj = self.registry("account.bank.statement.line")
        self.completion_rule_id = self.ref('account_statement_bankaccount_completion.bank_statement_completion_rule_10')
        self.journal_id = self.registry("ir.model.data").get_object_reference(self.cr, self. uid, "account", "bank_journal")[1]
        self.partner_id = self.ref('base.main_partner')
        # Create the profile
        self.account_id = self.registry("ir.model.data").get_object_reference(self.cr, self.uid, "account", "a_recv")[1]
        self.journal_id = self.registry("ir.model.data").get_object_reference(self.cr, self. uid, "account", "bank_journal")[1]
        self.profile_id = self.profile_obj.create(self.cr, self.uid, {
            "name": "TEST",
            "commission_account_id": self.account_id,
            "journal_id": self.journal_id,
            "rule_ids": [(6, 0, [self.completion_rule_id])]})
        # Create the completion rule

        # Create a bank statement
        self.statement_id = self.account_bank_statement_obj.create(self.cr, self.uid, {
            "balance_end_real": 0.0,
            "balance_start": 0.0,
            "date": time.strftime('%Y-%m-%d'),
            "journal_id": self.journal_id,
            "profile_id": self.profile_id

        })

        # Create bank a statement line
        self.statement_line_id = self.account_bank_statement_line_obj.create(self.cr, self.uid, {
            'amount': 1000.0,
            'name': 'EXT001',
            'ref': 'My ref',
            'statement_id': self.statement_id,
            'partner_acc_number': ACC_NUMBER
        })

        # Add a bank account number to the partner
        res_bank_obj = self.registry('res.partner.bank')
        res_bank_obj.create(self.cr, self.uid, {
                            "state": "bank",
                            "company_id": self.company_a.id,
                            "partner_id": self.partner_id,
                            "acc_number": ACC_NUMBER,
                            "footer": True,
                            "bank_name": "Reserve"
                            })

    def test_00(self):
        """Test complete partner_id from bank account number
        
        Test the automatic completion of the partner_id based on the account number associated to the
        statement line
        """
        self.prepare()
        statement_line = self.account_bank_statement_line_obj.browse(self.cr, self.uid, self.statement_line_id)
        # before import, the
        self.assertFalse(statement_line.partner_id, "Partner_id must be blank before completion")
        statement_obj = self.account_bank_statement_obj.browse(self.cr, self.uid, self.statement_id)
        statement_obj.button_auto_completion()
        statement_line = self.account_bank_statement_line_obj.browse(self.cr, self.uid, self.statement_line_id)
        self.assertEquals(self.partner_id, statement_line.partner_id['id'], "Missing expected partner id after completion")
