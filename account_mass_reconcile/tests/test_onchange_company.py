# © 2014-2016 Camptocamp SA (Damien Crier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestOnChange(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestOnChange, cls).setUpClass()
        acc_setting = cls.env["res.config.settings"]
        cls.acc_setting_obj = acc_setting.create({})
        cls.company_obj = cls.env["res.company"]
        # analytic defaults account creation
        cls.main_company = cls.env.ref("base.main_company")
        cls.sec_company = cls.company_obj.create(
            {"name": "Second company", "reconciliation_commit_every": 80}
        )

    def test_retrieve_analytic_account(self):
        sec_company_commit = self.sec_company.reconciliation_commit_every
        main_company_commit = self.main_company.reconciliation_commit_every

        self.acc_setting_obj.company_id = self.sec_company

        self.assertEqual(
            sec_company_commit, self.acc_setting_obj.reconciliation_commit_every, False
        )

        self.acc_setting_obj.company_id = self.main_company

        self.assertEqual(
            main_company_commit, self.acc_setting_obj.reconciliation_commit_every, False
        )
