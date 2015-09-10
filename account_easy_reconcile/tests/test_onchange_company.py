# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
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


class testOnChange(common.TransactionCase):

    def setUp(self):
        super(testOnChange, self).setUp()
        self.acc_setting_obj = self.registry('account.config.settings')
        self.company_obj = self.registry('res.company')
        # analytic defaults account creation
        self.main_company = self.ref('base.main_company')
        self.sec_company = self.company_obj.create(
            self.cr,
            self.uid,
            {
                'name': 'Second company',
                'reconciliation_commit_every': 80,
            }
            )

    def test_retrieve_analytic_account(self):
        sec_company_commit = self.company_obj.browse(
            self.cr,
            self.uid,
            self.sec_company).reconciliation_commit_every
        main_company_commit = self.company_obj.browse(
            self.cr,
            self.uid,
            self.main_company).reconciliation_commit_every

        res1 = self.acc_setting_obj.onchange_company_id(
            self.cr, self.uid, [], self.sec_company)

        self.assertEqual(sec_company_commit, res1.get(
            'value', {}).get('reconciliation_commit_every', False))

        res2 = self.acc_setting_obj.onchange_company_id(
            self.cr, self.uid, [], self.main_company)
        self.assertEqual(main_company_commit, res2.get(
            'value', {}).get('reconciliation_commit_every', False))
#         self.assertEqual(self.ref('account.analytic_agrolait'), res2.get(
#             'value', {}).get('reconciliation_commit_every', False))
