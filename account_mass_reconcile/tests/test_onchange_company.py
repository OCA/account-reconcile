# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Damien Crier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo import tools
from odoo.modules import get_module_resource


class TestOnChange(common.TransactionCase):

    def setUp(self):
        super(TestOnChange, self).setUp()
        tools.convert_file(self.cr, 'account',
                           get_module_resource('account', 'test',
                                               'account_minimal_test.xml'),
                           {}, 'init', False, 'test')
        acc_setting = self.env['account.config.settings']
        self.acc_setting_obj = acc_setting.create({})
        self.company_obj = self.env['res.company']
        # analytic defaults account creation
        self.main_company = self.env.ref('base.main_company')
        self.sec_company = self.company_obj.create(
            {
                'name': 'Second company',
                'reconciliation_commit_every': 80
            }
        )

    def test_retrieve_analytic_account(self):
        sec_company_commit = self.sec_company.reconciliation_commit_every
        main_company_commit = self.main_company.reconciliation_commit_every

        self.acc_setting_obj.company_id = self.sec_company

        self.assertEqual(sec_company_commit,
                         self.acc_setting_obj.reconciliation_commit_every,
                         False)

        self.acc_setting_obj.company_id = self.main_company

        self.assertEqual(main_company_commit,
                         self.acc_setting_obj.reconciliation_commit_every,
                         False)
