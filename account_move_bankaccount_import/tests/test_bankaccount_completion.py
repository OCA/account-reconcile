# -*- coding: utf-8 -*-
# © 2013 ACSONE SA/NV
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp.tests import common
from openerp import fields, tools
from openerp.modules import get_module_resource

ACC_NUMBER = " BE38 7330 4038 5372 "


class BankAccountCompletion(common.TransactionCase):

    def setUp(self):
        super(BankAccountCompletion, self).setUp()
        tools.convert_file(self.cr, 'account',
                           get_module_resource('account', 'test',
                                               'account_minimal_test.xml'),
                           {}, 'init', False, 'test')
        self.account_move_obj = self.env["account.move"]
        self.account_move_line_obj = \
            self.env["account.move.line"].with_context(
                check_move_validity=False
            )
        self.company_a = self.browse_ref('base.main_company')
        self.completion_rule_id = \
            self.ref('account_move_bankaccount_import.'
                     'bank_statement_completion_rule_10')
        self.journal = self.browse_ref("account.bank_journal")
        self.partner = self.browse_ref('base.main_partner')
        self.account_id = self.ref("account.a_recv")

        # Create the profile
        self.journal.write({
            'used_for_completion': True,
            'rule_ids': [(6, 0, [self.completion_rule_id])]
        })
        # Create a bank statement
        self.move = self.account_move_obj.create({
            "date": fields.Date.today(),
            "journal_id": self.journal.id
        })

        # Add a bank account number to the partner
        self.res_partner_bank_obj = self.env['res.partner.bank']
        vals = {"state": "bank",
                "company_id": self.company_a.id,
                "partner_id": self.partner.id,
                "acc_number": ACC_NUMBER,
                "footer": True,
                "bank_name": "Reserve",
                }
        self.partner_bank = self.res_partner_bank_obj.create(vals)

    def test_00(self):
        """Test complete partner_id from bank account number
        Test the automatic completion of the partner_id based on the account
        number associated to the statement line
        """
        for bank_acc_number in [ACC_NUMBER, ACC_NUMBER.replace(" ", ""),
                                ACC_NUMBER.replace(" ", "-")]:
            # check the completion for well formatted and not well
            # formatted account number
            self.partner_bank.write({"acc_number": bank_acc_number})
            for acc_number in [ACC_NUMBER, ACC_NUMBER.replace(" ", ""),
                               ACC_NUMBER.replace(" ", "-"),
                               " BE38-7330 4038-5372 "]:
                self.move_line = self.account_move_line_obj.create({
                    'account_id': self.account_id,
                    'credit': 1000.0,
                    'name': 'EXT001',
                    'move_id': self.move.id,
                    'partner_acc_number': acc_number
                })
                self.assertFalse(
                    self.move_line.partner_id,
                    'Partner_id must be blank before completion')
                self.move.button_auto_completion()
                self.assertEquals(
                    self.partner, self.move_line.partner_id,
                    "Missing expected partner id after completion")

            self.move_line = self.account_move_line_obj.create({
                'account_id': self.account_id,
                'credit': 1000.0,
                'name': 'EXT001',
                'move_id': self.move.id,
                'partner_acc_number': 'BE38a7330.4038-5372.',
            })
            self.assertFalse(self.move_line.partner_id,
                             'Partner_id must be blank before completion')
            self.move.button_auto_completion()
            self.assertFalse(self.move_line.partner_id)
