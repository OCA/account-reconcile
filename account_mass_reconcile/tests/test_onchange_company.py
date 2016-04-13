# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Damien Crier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


class TestOnChange(common.TransactionCase):

    def setUp(self):
        super(TestOnChange, self).setUp()
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
