# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV <http://therp.nl>.
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
from openerp.tests.common import TransactionCase
from openerp import exceptions


class TestAccountReconcileDifferentPartners(TransactionCase):
    def test_account_reconcile_different_partners(self):
        # _register_hooks are only called after tests
        self.env['account.move.reconcile']._register_hook()
        move_data = {
            'line_id': [
                (0, 0, {
                    'name': 'test1',
                    'account_id': self.env['account.account'].search([
                        ('reconcile', '=', True), ('type', '=', 'receivable'),
                    ])[:1].id,
                    'credit': 42,
                    'partner_id': self.env.ref('base.res_partner_2').id,
                }),
                (0, 0, {
                    'name': 'test2',
                    'account_id': self.env['account.account'].search([
                        ('reconcile', '=', True), ('type', '=', 'receivable'),
                    ])[:1].id,
                    'debit': 42,
                    'partner_id': self.env.ref('base.res_partner_7').id,
                }),
            ],
            'journal_id': self.env['account.journal'].search([])[:1].id,
        }
        # this should work
        self.env['account.move'].create(move_data).line_id.reconcile()
        with self.assertRaises(exceptions.ValidationError):
            # while this still should raise
            self.env['account.move'].create(move_data)\
                .sudo(self.env.ref('base.user_demo').id).line_id.reconcile()
