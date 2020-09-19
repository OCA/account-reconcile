# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAccountBankStatementPostprocessModel(TransactionCase):
    def setUp(self):
        super().setUp()

        self.currency_usd = self.env.ref("base.USD")
        self.currency_eur = self.env.ref("base.EUR")
        self.AccountJournal = self.env["account.journal"]
        self.AccountBankStatement = self.env["account.bank.statement"]
        self.AccountBankStatementLine = self.env["account.bank.statement.line"]
        self.AccountBankStatementPostprocessModel = self.env[
            "account.bank.statement.postprocess.model"
        ]

    def test_extract_fee_percent(self):
        journal = self.AccountJournal.create({
            "name": "Bank",
            "type": "bank",
            "code": "BANK",
            "currency_id": self.currency_usd.id,
        })
        statement = self.AccountBankStatement.create({
            "name": "Statement",
            "journal_id": journal.id,
        })
        line = self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "TRANSACTION (+ 1.00%)",
            "amount": "100.0",
            "amount_currency": "85.0",
            "currency_id": self.currency_eur.id,
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION-ID",
        })
        model = self.AccountBankStatementPostprocessModel.create({
            "name": "Postprocess Model",
            "postprocess_type": "extract_fee",
            "match_field": "name",
            "match_regexp": r"\(\+\s+(?P<FEE_PERCENT>[\d.,]+)%\)",
        })

        model.apply(line)

        self.assertEqual(len(statement.line_ids), 2)
        self.assertEqual(line.amount, 99.0)

        fee_line = statement.line_ids - line
        self.assertEqual(fee_line.amount, 1.00)
        self.assertEqual(fee_line.name, "Extracted Fee: TRANSACTION (+ 1.00%)")

    def test_extract_fee(self):
        journal = self.AccountJournal.create({
            "name": "Bank",
            "type": "bank",
            "code": "BANK",
            "currency_id": self.currency_usd.id,
        })
        statement = self.AccountBankStatement.create({
            "name": "Statement",
            "journal_id": journal.id,
        })
        line = self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "TRANSACTION (+ 1.00)",
            "amount": "100.0",
            "amount_currency": "85.0",
            "currency_id": self.currency_eur.id,
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION-ID",
        })
        model = self.AccountBankStatementPostprocessModel.create({
            "name": "Postprocess Model",
            "postprocess_type": "extract_fee",
            "match_field": "name",
            "match_regexp": r"\(\+\s+(?P<FEE>[\d.,]+)\)",
        })

        model.apply(line)

        self.assertEqual(len(statement.line_ids), 2)
        self.assertEqual(line.amount, 99.0)

        fee_line = statement.line_ids - line
        self.assertEqual(fee_line.amount, 1.00)
        self.assertEqual(fee_line.name, "Extracted Fee: TRANSACTION (+ 1.00)")

    def test_extract_fee_custom_description(self):
        journal = self.AccountJournal.create({
            "name": "Bank",
            "type": "bank",
            "code": "BANK",
            "currency_id": self.currency_usd.id,
        })
        statement = self.AccountBankStatement.create({
            "name": "Statement",
            "journal_id": journal.id,
        })
        line = self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "TRANSACTION (+ 1.00)",
            "amount": "100.0",
            "amount_currency": "85.0",
            "currency_id": self.currency_eur.id,
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION-ID",
        })
        model = self.AccountBankStatementPostprocessModel.create({
            "name": "Postprocess Model",
            "postprocess_type": "extract_fee",
            "match_field": "name",
            "match_regexp": r"\(\+\s+(?P<FEE>[\d.,]+)\)",
            "other_value": "Custom: %()s",
        })

        model.apply(line)

        self.assertEqual(len(statement.line_ids), 2)

        fee_line = statement.line_ids - line
        self.assertEqual(fee_line.name, "Custom: TRANSACTION (+ 1.00)")

    def test_multi_currency(self):
        journal = self.AccountJournal.create({
            "name": "Bank",
            "type": "bank",
            "code": "BANK",
            "currency_id": self.currency_usd.id,
        })
        statement = self.AccountBankStatement.create({
            "name": "Statement",
            "journal_id": journal.id,
        })
        line = self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "TRANSACTION (85.00 EUR)",
            "amount": "100.0",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION-ID",
        })
        model = self.AccountBankStatementPostprocessModel.create({
            "name": "Postprocess Model",
            "postprocess_type": "multi_currency",
            "match_field": "name",
            "match_regexp": (
                r"\((?P<AMOUNT_CURRENCY>[\d.,]+)\s+(?P<CURRENCY>[A-Z]{3})\)"
            ),
        })

        model.apply(line)

        self.assertEqual(len(statement.line_ids), 1)
        self.assertEqual(line.amount, 100.0)
        self.assertEqual(line.amount_currency, 85.0)
        self.assertEqual(line.currency_id, self.currency_eur)

    def test_multi_currency_with_fee(self):
        journal = self.AccountJournal.create({
            "name": "Bank",
            "type": "bank",
            "code": "BANK",
            "currency_id": self.currency_eur.id,
        })
        statement = self.AccountBankStatement.create({
            "name": "Statement",
            "journal_id": journal.id,
        })
        line = self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "TRANSACTION (56.00 USD + 0.56, 0.8830357)",
            "amount": "-49.94",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION-ID",
        })
        model = self.AccountBankStatementPostprocessModel.create({
            "name": "Multi-Currency (Fee Included)",
            "postprocess_type": "multi_currency_with_fee",
            "match_field": "name",
            "match_regexp": (
                r"\s*\((?P<AMOUNT_CURRENCY>[\d.,]+)\s+(?P<CURRENCY>[A-Z]{3})"
                r"\s+\+\s+(?P<FEE>[\d.,]+),\s+"
                r"(?P<EXCHANGE_RATE>[\d.,]+)\)"
            ),
        })

        model.apply(line)

        self.assertEqual(len(statement.line_ids), 2)
        fee_line = statement.line_ids - line

        self.assertEqual(line.amount, -49.45)
        self.assertEqual(line.amount_currency, -56.0)
        self.assertEqual(line.currency_id, self.currency_usd)

        self.assertEqual(fee_line.amount, -0.49)
        self.assertEqual(fee_line.amount_currency, 0.0)
        self.assertFalse(fee_line.currency_id)
        self.assertEqual(
            fee_line.name,
            "Extracted Fee: TRANSACTION (56.00 USD + 0.56, 0.8830357)"
        )

    def test_multi_currency_with_fee_percent(self):
        journal = self.AccountJournal.create({
            "name": "Bank",
            "type": "bank",
            "code": "BANK",
            "currency_id": self.currency_eur.id,
        })
        statement = self.AccountBankStatement.create({
            "name": "Statement",
            "journal_id": journal.id,
        })
        line = self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "TRANSACTION (56.00 USD, 0.8830357)",
            "amount": "-49.94",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION-ID",
        })
        model = self.AccountBankStatementPostprocessModel.create({
            "name": "Multi-Currency (Fee Included)",
            "postprocess_type": "multi_currency_with_fee",
            "match_field": "name",
            "match_regexp": (
                r"\s*\((?P<AMOUNT_CURRENCY>[\d.,]+)\s+(?P<CURRENCY>[A-Z]{3}),"
                r"\s+(?P<EXCHANGE_RATE>[\d.,]+)\)"
            ),
        })

        model.apply(line)

        self.assertEqual(len(statement.line_ids), 2)
        fee_line = statement.line_ids - line

        self.assertEqual(line.amount, -49.45)
        self.assertEqual(line.amount_currency, -56.0)
        self.assertEqual(line.currency_id, self.currency_usd)

        self.assertEqual(fee_line.amount, -0.49)
        self.assertEqual(fee_line.amount_currency, 0.0)
        self.assertFalse(fee_line.currency_id)
        self.assertEqual(
            fee_line.name,
            "Extracted Fee: TRANSACTION (56.00 USD, 0.8830357)"
        )

    def test_multi_currency_with_fee_custom_description(self):
        journal = self.AccountJournal.create({
            "name": "Bank",
            "type": "bank",
            "code": "BANK",
            "currency_id": self.currency_eur.id,
        })
        statement = self.AccountBankStatement.create({
            "name": "Statement",
            "journal_id": journal.id,
        })
        line = self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "TRANSACTION (56.00 USD, 0.8830357)",
            "amount": "-49.94",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION-ID",
        })
        model = self.AccountBankStatementPostprocessModel.create({
            "name": "Multi-Currency (Fee Included)",
            "postprocess_type": "multi_currency_with_fee",
            "match_field": "name",
            "match_regexp": (
                r"\s*\((?P<AMOUNT_CURRENCY>[\d.,]+)\s+(?P<CURRENCY>[A-Z]{3}),"
                r"\s+(?P<EXCHANGE_RATE>[\d.,]+)\)"
            ),
            "other_value": "Custom: %()s",
        })

        model.apply(line)

        self.assertEqual(len(statement.line_ids), 2)
        fee_line = statement.line_ids - line

        self.assertEqual(line.amount, -49.45)
        self.assertEqual(line.amount_currency, -56.0)
        self.assertEqual(line.currency_id, self.currency_usd)

        self.assertEqual(fee_line.amount, -0.49)
        self.assertEqual(fee_line.amount_currency, 0.0)
        self.assertFalse(fee_line.currency_id)
        self.assertEqual(
            fee_line.name,
            "Custom: TRANSACTION (56.00 USD, 0.8830357)"
        )

    def test_trim_field(self):
        journal = self.AccountJournal.create({
            "name": "Bank",
            "type": "bank",
            "code": "BANK",
            "currency_id": self.currency_usd.id,
        })
        statement = self.AccountBankStatement.create({
            "name": "Statement",
            "journal_id": journal.id,
        })
        line = self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "TRANSACTION (JUNK)",
            "amount": "100.0",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION-ID",
        })
        model = self.AccountBankStatementPostprocessModel.create({
            "name": "Postprocess Model",
            "postprocess_type": "trim_field",
            "match_field": "name",
            "match_regexp": r"\s+\(JUNK\)",
        })

        model.apply(line)

        self.assertEqual(line.name, "TRANSACTION")

    def test_trim_field_groups(self):
        journal = self.AccountJournal.create({
            "name": "Bank",
            "type": "bank",
            "code": "BANK",
            "currency_id": self.currency_usd.id,
        })
        statement = self.AccountBankStatement.create({
            "name": "Statement",
            "journal_id": journal.id,
        })
        line = self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "TRANSACTION (JUNK)",
            "amount": "100.0",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION-ID",
        })
        model = self.AccountBankStatementPostprocessModel.create({
            "name": "Postprocess Model",
            "postprocess_type": "trim_field",
            "match_field": "name",
            "match_regexp": r"(?:TRANSACTION)( \(JUNK\))",
        })

        model.apply(line)

        self.assertEqual(line.name, "TRANSACTION")

    def test_append_field(self):
        journal = self.AccountJournal.create({
            "name": "Bank",
            "type": "bank",
            "code": "BANK",
            "currency_id": self.currency_usd.id,
        })
        statement = self.AccountBankStatement.create({
            "name": "Statement",
            "journal_id": journal.id,
        })
        line = self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "TRANSACTION",
            "amount": "100.0",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION-ID",
        })
        model = self.AccountBankStatementPostprocessModel.create({
            "name": "Postprocess Model",
            "postprocess_type": "append_field",
            "match_field": "name",
            "match_regexp": r".*",
            "other_field": "note"
        })

        model.apply(line)

        self.assertEqual(line.name, "TRANSACTION; NOTE")

    def test_merge_per_statement(self):
        journal = self.AccountJournal.create({
            "name": "Bank",
            "type": "bank",
            "code": "BANK",
            "currency_id": self.currency_usd.id,
        })
        statement = self.AccountBankStatement.create({
            "name": "Statement",
            "journal_id": journal.id,
        })
        self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "TRANSACTION1",
            "amount": "100.0",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION1-ID",
        })
        self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "TRANSACTION2",
            "amount": "200.0",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION2-ID",
        })
        model = self.AccountBankStatementPostprocessModel.create({
            "name": "Postprocess Model",
            "postprocess_type": "merge_per_statement",
            "match_field": "name",
            "match_regexp": "TRANSACTION",
        })

        model.apply(statement.line_ids)

        self.assertEqual(len(statement.line_ids), 1)
        self.assertEqual(statement.line_ids.name, "Merged Transaction")
        self.assertEqual(statement.line_ids.amount, 300.0)

    def test_merge_per_statement_custom_description(self):
        journal = self.AccountJournal.create({
            "name": "Bank",
            "type": "bank",
            "code": "BANK",
            "currency_id": self.currency_usd.id,
        })
        statement = self.AccountBankStatement.create({
            "name": "Statement",
            "journal_id": journal.id,
        })
        self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "EXCHANGE1",
            "amount": "100.0",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "EXCHANGE1-ID",
        })
        self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "FEE1",
            "amount": "1.0",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "FEE1-ID",
        })
        self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "EXCHANGE2",
            "amount": "50.0",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "EXCHANGE2-ID",
        })
        self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "FEE2",
            "amount": "0.5",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "FEE2-ID",
        })
        model_1 = self.AccountBankStatementPostprocessModel.create({
            "name": "Postprocess Model 1",
            "postprocess_type": "merge_per_statement",
            "match_field": "name",
            "match_regexp": "FEE",
            "other_value": "Merged Fee",
        })
        model_2 = self.AccountBankStatementPostprocessModel.create({
            "name": "Postprocess Model 2",
            "postprocess_type": "merge_per_statement",
            "match_field": "name",
            "match_regexp": "EXCHANGE",
            "other_value": "Merged Exchange",
        })

        (model_1 | model_2).apply(statement.line_ids)

        self.assertEqual(len(statement.line_ids), 2)

    def test_delete(self):
        journal = self.AccountJournal.create({
            "name": "Bank",
            "type": "bank",
            "code": "BANK",
            "currency_id": self.currency_usd.id,
        })
        statement = self.AccountBankStatement.create({
            "name": "Statement",
            "journal_id": journal.id,
        })
        line = self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "TRANSACTION",
            "amount": "100.0",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION-ID",
        })
        self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "TRANSACTION2",
            "amount": "200.0",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION2-ID",
        })
        model = self.AccountBankStatementPostprocessModel.create({
            "name": "Postprocess Model",
            "postprocess_type": "delete",
            "match_field": "name",
            "match_regexp": "TRANSACTION2",
        })

        model.apply(statement.line_ids)

        self.assertEqual(statement.line_ids, line)

    def test_apply_on_import(self):
        self.AccountBankStatementPostprocessModel.create({
            "name": "Postprocess Model",
            "postprocess_type": "trim_field",
            "match_field": "name",
            "match_regexp": r"(?:TRANSACTION)( \(JUNK\))",
            "apply_on_import": True,
        })

        journal = self.AccountJournal.create({
            "name": "Bank",
            "type": "bank",
            "code": "BANK",
            "currency_id": self.currency_usd.id,
        })
        statement = self.AccountBankStatement.create({
            "name": "Statement",
            "journal_id": journal.id,
        })
        line = self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "TRANSACTION (JUNK)",
            "amount": "100.0",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION-ID",
        })

        self.assertEqual(line.name, "TRANSACTION")

    def test_combined_models(self):
        journal = self.AccountJournal.create({
            "name": "Bank",
            "type": "bank",
            "code": "BANK",
            "currency_id": self.currency_eur.id,
        })
        statement = self.AccountBankStatement.create({
            "name": "Statement",
            "journal_id": journal.id,
        })
        line = self.AccountBankStatementLine.create({
            "statement_id": statement.id,
            "name": "TRANSACTION (56.00 USD + 1.0%, 0.8830357)",
            "amount": "-49.94",
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION-ID",
        })
        multi_currency = self.AccountBankStatementPostprocessModel.create({
            "name": "Multi-Currency",
            "postprocess_type": "multi_currency",
            "match_field": "name",
            "match_regexp": (
                r"\s*\((?P<AMOUNT_CURRENCY>[\d.,]+)\s+(?P<CURRENCY>[A-Z]{3})\s+"
                r"\+\s+(?:[\d.,]+)%,\s+(?:[\d.,]+)\)"
            ),
        })
        extract_fee = self.AccountBankStatementPostprocessModel.create({
            "name": "Extract Fee",
            "postprocess_type": "extract_fee",
            "match_field": "name",
            "match_regexp": (
                r"\s*\((?:[\d.,]+)\s+(?:[A-Z]{3})\s+\+\s+"
                r"(?P<FEE_PERCENT>[\d.,]+)%,\s+(?:[\d.,]+)\)"
            ),
        })

        (multi_currency | extract_fee).apply(line)

        self.assertEqual(len(statement.line_ids), 2)
        fee_line = statement.line_ids - line

        self.assertEqual(line.amount, -49.44)
        self.assertEqual(line.amount_currency, -56.0)
        self.assertEqual(line.currency_id, self.currency_usd)

        self.assertEqual(fee_line.amount, -0.50)
        self.assertEqual(fee_line.amount_currency, 0.0)
        self.assertFalse(fee_line.currency_id)
