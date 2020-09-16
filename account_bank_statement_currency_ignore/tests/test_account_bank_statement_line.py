# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestAccountBankStatementLine(TransactionCase):
    def setUp(self):
        super().setUp()

        self.currency_usd = self.env.ref("base.USD")
        self.currency_eur = self.env.ref("base.EUR")
        self.currency_chf = self.env.ref("base.CHF")
        self.AccountJournal = self.env["account.journal"]
        self.AccountBankStatement = self.env["account.bank.statement"]
        self.AccountBankStatementLine = self.env["account.bank.statement.line"]

    def test_create(self):
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
            "amount_currency": "85.0",
            "currency_id": self.currency_eur.id,
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION-ID",
        })

        self.assertEqual(line.amount_currency, 85.0)
        self.assertEqual(line.currency_id, self.currency_eur)
        self.assertEqual(line.original_amount_currency, 85.0)
        self.assertEqual(line.original_currency_id, self.currency_eur)

    def test_create_ignored(self):
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
        with self.assertRaises(UserError):
            self.AccountBankStatementLine.create({
                "statement_id": statement.id,
                "name": "TRANSACTION",
                "amount": "100.0",
                "amount_currency": "85.0",
                "currency_id": self.currency_eur.id,
                "ignore_currency": True,
                "date": "2020-09-01",
                "note": "NOTE",
                "unique_import_id": "TRANSACTION-ID",
            })

    def test_create_ignored_original(self):
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
            "original_amount_currency": "85.0",
            "original_currency_id": self.currency_eur.id,
            "ignore_currency": True,
            "date": "2020-09-01",
            "note": "NOTE",
            "unique_import_id": "TRANSACTION-ID",
        })
        self.assertEqual(line.amount_currency, 0.0)
        self.assertFalse(line.currency_id)
        self.assertEqual(line.original_amount_currency, 85.0)
        self.assertEqual(line.original_currency_id, self.currency_eur)

        line.action_toggle_ignore_currency()
        self.assertEqual(line.amount_currency, 85.0)
        self.assertEqual(line.currency_id, self.currency_eur)
        self.assertEqual(line.original_amount_currency, 85.0)
        self.assertEqual(line.original_currency_id, self.currency_eur)
