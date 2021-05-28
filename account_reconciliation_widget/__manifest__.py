# Copyright 2020 Ozono Multimedia - Iván Antón
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "account_reconciliation_widget",
    "version": "14.0.1.1.5",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Account reconciliation widget",
    "author": "Odoo, Ozono Multimedia, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/account_bank_statement.xml",
        "views/account_bank_statement_line.xml",
        "views/account_journal.xml",
    ],
    "qweb": [
        "static/src/xml/account_reconciliation.xml",
    ],
    "installable": True,
}
