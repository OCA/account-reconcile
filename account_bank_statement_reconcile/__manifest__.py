# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Accounting: Bank Statement Reconcile actions",
    "summary": "Menu items to perform reconcile actions on selected records.",
    "version": "12.0.1.0.0",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-reconcile",
    "author": "CorporateHub, Odoo Community Association (OCA)",
    "maintainers": ["alexey-pelykh"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        "views/account_bank_statement_line.xml",
        "views/account_bank_statement.xml",
    ],
}
