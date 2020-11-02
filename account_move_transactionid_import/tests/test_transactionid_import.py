# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import base64
import os

from odoo.modules.module import get_module_resource
from odoo.addons.account_move_base_import.tests.test_base_import import (
    TestCodaImport,
)


class TestTransactionIdImport(TestCodaImport):
    def test_multiline_csv_multi_move(self):
        """Test import from csv
        """
        self.journal.write(
            {
                "import_type": "generic_csvxls_transaction",
            }
        )
        file_name = get_module_resource(
            "account_move_transactionid_import",
            "tests",
            "data",
            "statement.csv"
        )
        import_action = self._import_file_multi(file_name)
        moves = self.account_move_obj.browse(import_action["domain"][0][2])
        self._validate_transactionid_imported_moves(moves)

    def test_multiline_xls_multi_move(self):
        """Test import from xls
        """
        self.journal.write(
            {
                "import_type": "generic_csvxls_transaction",
            }
        )
        file_name = get_module_resource(
            "account_move_transactionid_import",
            "tests",
            "data",
            "statement.xls"
        )
        import_action = self._import_file_multi(file_name)
        moves = self.account_move_obj.browse(import_action["domain"][0][2])
        self._validate_transactionid_imported_moves(moves)

    def test_multiline_csv_single_move(self):
        """Test import from csv
        """
        self.journal.write(
            {
                "import_type": "generic_csvxls_transaction_single",
            }
        )
        file_name = get_module_resource(
            "account_move_transactionid_import",
            "tests",
            "data",
            "statement.csv"
        )
        import_action = self._import_file_multi(file_name)
        move = self.account_move_obj.browse(import_action["res_id"])
        self._validate_transactionid_imported_move(move)

    def test_multiline_xls_single_move(self):
        """Test import from xls
        """
        self.journal.write(
            {
                "import_type": "generic_csvxls_transaction_single",
            }
        )
        file_name = get_module_resource(
            "account_move_transactionid_import",
            "tests",
            "data",
            "statement.xls"
        )
        import_action = self._import_file_multi(file_name)
        move = self.account_move_obj.browse(import_action["res_id"])
        self._validate_transactionid_imported_move(move)

    def _import_file_multi(self, file_name):
        """ import a file using the wizard
        return the create account.bank.statement object
        """
        content = ""
        with open(file_name, "rb") as f:
            content = f.read()
        self.wizard = self.import_wizard_obj.create(
            {
                "journal_id": self.journal.id,
                "input_statement": base64.b64encode(content),
                "file_name": os.path.basename(file_name),
            }
        )
        return self.wizard.import_statement()

    def _validate_transactionid_imported_moves(self, moves):
        self.assertEqual(len(moves), 3)
        transaction_ids = ["50969286", "51065326", "51179306"]
        for i, move in enumerate(moves):
            self.assertEqual(move.name, transaction_ids[i])
            self.assertEqual(move.ref, "statement")
            self.assertEqual(3, len(move.line_ids))

    def _validate_transactionid_imported_move(self, move):
        self.assertEqual(len(move), 1)
        transaction_ids = ["50969286", "51065326", "51179306"]
        self.assertEqual(move.ref, "statement")
        for idx, line in enumerate(move.line_ids):
            self.assertEqual(line.name, transaction_ids[idx])
        self.assertEqual(len(move.line_ids), 5)
