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

ACC_NUMBER = " BE38 7330 4038 5372 "


class bankaccount_completion(common.TransactionCase):

    def setUp(self):
        super(bankaccount_completion, self).setUp()
        self.company_a = self.browse_ref('base.main_company')
        self.profile_obj = self.registry("account.statement.profile")
        self.acc_bk_stmt = self.registry("account.bank.statement")
        self.st_line_obj = self.registry("account.bank.statement.line")
        self.completion_rule_id = \
            self.ref('account_statement_bankaccount_completion.'
                     'bank_statement_completion_rule_10')
        self.journal_id = self.ref("account.bank_journal")
        self.partner_id = self.ref('base.main_partner')
        self.account_id = self.ref("account.a_recv")

        # Create the profile
        self.profile_id = self.profile_obj.create(self.cr, self.uid, {
            "name": "TEST",
            "commission_account_id": self.account_id,
            "journal_id": self.journal_id,
            "rule_ids": [(6, 0, [self.completion_rule_id])]})
        # Create a bank statement
        vals = {"balance_end_real": 0.0,
                "balance_start": 0.0,
                "date": time.strftime('%Y-%m-%d'),
                "journal_id": self.journal_id,
                "profile_id": self.profile_id,
                }
        self.statement_id = self.acc_bk_stmt.create(self.cr,
                                                    self.uid,
                                                    vals)

        # Add a bank account number to the partner
        self.res_partner_bank_obj = self.registry('res.partner.bank')
        vals = {"state": "bank",
                "company_id": self.company_a.id,
                "partner_id": self.partner_id,
                "acc_number": ACC_NUMBER,
                "footer": True,
                "bank_name": "Reserve",
                }
        self.res_partner_bank_id = self.res_partner_bank_obj.create(self.cr,
                                                                    self.uid,
                                                                    vals)

    def test_00(self):
        """Test complete partner_id from bank account number
        Test the automatic completion of the partner_id based on the account
        number associated to the statement line
        """
        for bank_acc_number in [ACC_NUMBER, ACC_NUMBER.replace(" ", ""),
                                ACC_NUMBER.replace(" ", "-")]:
            # check the completion for well formatted and not well
            # formatted account number
            self.res_partner_bank_obj.write(self.cr,
                                            self.uid,
                                            self.res_partner_bank_id,
                                            {"acc_number": bank_acc_number}
                                            )
            for acc_number in [ACC_NUMBER, ACC_NUMBER.replace(" ", ""),
                               ACC_NUMBER.replace(" ", "-"),
                               " BE38-7330 4038-5372 "]:
                vals = {'amount': 1000.0,
                        'name': 'EXT001',
                        'ref': 'My ref',
                        'statement_id': self.statement_id,
                        'partner_acc_number': acc_number
                        }
                line_id = self.st_line_obj.create(self.cr, self.uid, vals)
                line = self.st_line_obj.browse(self.cr, self.uid, line_id)
                self.assertFalse(line.partner_id,
                                 'Partner_id must be blank before completion')
                statement_obj = self.acc_bk_stmt.browse(self.cr,
                                                        self.uid,
                                                        self.statement_id)
                statement_obj.button_auto_completion()
                line = self.st_line_obj.browse(self.cr, self.uid, line_id)
                self.assertEquals(self.partner_id, line.partner_id['id'],
                                  'Missing expected partner id after '
                                  'completion')
            vals = {'amount': 1000.0,
                    'name': 'EXT001',
                    'ref': 'My ref',
                    'statement_id': self.statement_id,
                    'partner_acc_number': 'BE38a7330.4038-5372.',
                    }
            line_id = self.st_line_obj.create(self.cr, self.uid, vals)
            line = self.st_line_obj.browse(self.cr, self.uid, line_id)
            self.assertFalse(line.partner_id,
                             'Partner_id must be blank before completion')
            statement_obj = self.acc_bk_stmt.browse(self.cr,
                                                    self.uid,
                                                    self.statement_id)
            statement_obj.button_auto_completion()
            line = self.st_line_obj.browse(self.cr, self.uid, line_id)
            self.assertFalse(line.partner_id.id)
