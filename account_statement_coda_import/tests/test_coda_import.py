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
import inspect
import os
import base64


class test_coda_import(common.TransactionCase):

    def prepare(self):
        self.company_a = self.browse_ref('base.main_company')
        self.profile_obj = self.registry("account.statement.profile")
        self.account_bank_statement_obj = self.registry("account.bank.statement")
        filscalyear_obj = self.registry("account.fiscalyear")
        # create the 2011 fiscal year since imported coda file reference statement lines in 2009
        self.fiscalyear_id = self._create_fiscalyear("2009", self.company_a.id)

        self.account_id = self.registry("ir.model.data").get_object_reference(self.cr, self.uid, "account", "a_recv")[1]
        self.journal_id = self.registry("ir.model.data").get_object_reference(self.cr, self. uid, "account", "bank_journal")[1]
        self.import_wizard_obj = self.registry('credit.statement.import')
        self.profile_id = self.profile_obj.create(self.cr, self.uid, {
            "name": "CODA_PROFILE",
            "commission_account_id": self.account_id,
            "journal_id": self.journal_id,
            "import_type": "coda_transaction"})

    def _create_fiscalyear(self, year, company_id):
        fiscalyear_obj = self.registry("account.fiscalyear")
        fiscalyear_id = fiscalyear_obj.create(self.cr, self.uid, {
            "name": year,
            "code": year,
            "date_start": year + "-01-01",
            "date_stop": year + "-12-31",
            "company_id": company_id
        })
        fiscalyear_obj.create_period3(self.cr, self.uid, [fiscalyear_id])
        return fiscalyear_id

    def _filename_to_abs_filename(self, file_name):
        dir_name = os.path.dirname(inspect.getfile(self.__class__))
        return os.path.join(dir_name, file_name)

    def _import_coda_file(self, file_name):
        """ import a coda file using the wizard
        
        return the create account.bank.statement object
        """
        with open(file_name) as f:
            content = f.read()
            wizard_id = self.import_wizard_obj.create(self.cr, self.uid, {
                "profile_id": self.profile_id,
                'input_statement': base64.b64encode(content),
                'file_name': os.path.basename(file_name),
            })
            res = self.import_wizard_obj.import_statement(self.cr, self.uid, wizard_id)
            statement_id = self.account_bank_statement_obj.search(self.cr, self.uid, eval(res['domain']))
            return self.account_bank_statement_obj.browse(self.cr, self.uid, statement_id)[0]

    def test_00(self):
        """Test import from CODA 2.3
        """
        self.prepare()
        file_name = self._filename_to_abs_filename("Dummy_testbestand_coda_iban_v2_3.txt")
        statement = self._import_coda_file(file_name)
        self.assertEqual(30, len(statement.line_ids))
