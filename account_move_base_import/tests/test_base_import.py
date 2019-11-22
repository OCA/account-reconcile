# Copyright 2011-2016 Akretion
# Copyright 2011-2019 Camptocamp SA
# Copyright 2013 Savoir-faire Linux
# Copyright 2014 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import base64
import os
from operator import attrgetter
from odoo.tests import common
from odoo import tools, fields
from odoo.modules import get_resource_path


class TestCodaImport(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.company_a = self.browse_ref('base.main_company')
        tools.convert_file(self.cr, 'account',
                           get_resource_path('account', 'test',
                                             'account_minimal_test.xml'),
                           {}, 'init', False, 'test')
        self.account_move_obj = self.env["account.move"]
        self.account_move_line_obj = self.env["account.move.line"]
        self.account_id = self.ref("account.a_recv")
        self.journal = self.browse_ref("account.bank_journal")
        self.import_wizard_obj = self.env['credit.statement.import']
        self.partner = self.browse_ref("base.res_partner_12")
        self.journal.write({
            'used_for_import': True,
            "import_type": "generic_csvxls_so",
            'partner_id': self.partner.id,
            'commission_account_id': self.account_id,
            'receivable_account_id': self.account_id,
            'create_counterpart': True,
        })

    def _import_file(self, file_name):
        """ import a file using the wizard
        return the create account.bank.statement object
        """
        with open(file_name, 'rb') as f:
            content = f.read()
            self.wizard = self.import_wizard_obj.create({
                "journal_id": self.journal.id,
                'input_statement': base64.b64encode(content),
                'file_name': os.path.basename(file_name),
            })
            res = self.wizard.import_statement()
            return self.account_move_obj.browse(res['res_id'])

    def test_simple_xls(self):
        """Test import from xls
        """
        file_name = get_resource_path(
            'account_move_base_import',
            'tests',
            'data',
            'statement.xls'
        )
        move = self._import_file(file_name)
        self._validate_imported_move(move)

    def test_simple_csv(self):
        """Test import from csv
        """
        file_name = get_resource_path(
            'account_move_base_import',
            'tests',
            'data',
            'statement.csv'
        )
        move = self._import_file(file_name)
        self._validate_imported_move(move)

    def _validate_imported_move(self, move):
        self.assertEqual("/", move.name)
        self.assertEqual(5, len(move.line_ids))
        move_line = sorted(move.line_ids,
                           key=attrgetter('date_maturity'))[2]
        # common infos
        self.assertEqual(
            move_line.date_maturity, fields.Date.from_string('2011-03-07')
        )
        self.assertEqual(move_line.credit, 118.4)
        self.assertEqual(move_line.name, "label a")
