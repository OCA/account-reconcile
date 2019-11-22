# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import base64
import os

from odoo.modules.module import get_module_resource
from odoo.addons.account_move_base_import.tests.test_base_import import (
    TestCodaImport,
)


class TestTransactionIdImport(TestCodaImport):
    def test_multiline_csv(self):
        """Test import from csv
        """
        self.journal.write({"import_type": "generic_csvxls_transaction"})
        file_name = get_module_resource(
            "account_move_transactionid_import",
            "tests",
            "data",
            "statement.csv"
        )
        move_ids = self._import_file_multi(file_name)
        self._validate_imported_moves(move_ids)

    def test_multiline_xls(self):
        """Test import from xls
        """
        self.journal.write({"import_type": "generic_csvxls_transaction"})
        file_name = get_module_resource(
            "account_move_transactionid_import",
            "tests",
            "data",
            "statement.xls"
        )
        move_ids = self._import_file_multi(file_name)
        self._validate_imported_moves(move_ids)

    def _import_file_multi(self, file_name):
        """ import a file using the wizard
        return the create account.bank.statement object
        """
        with open(file_name, "rb") as f:
            content = f.read()
            self.wizard = self.import_wizard_obj.create(
                {
                    "journal_id": self.journal.id,
                    "input_statement": base64.b64encode(content),
                    "file_name": os.path.basename(file_name),
                }
            )
            res = self.wizard.import_statement()
            return self.account_move_obj.browse(res["domain"][0][2])

    def _validate_imported_moves(self, moves):
        self.assertEqual(len(moves), 3)
        transaction_ids = ["50969286", "51065326", "51179306"]
        for i, move in enumerate(moves):
            self.assertEqual(move.ref, transaction_ids[i])
            self.assertEqual(move.name, "statement")
            self.assertEqual(3, len(move.line_ids))
