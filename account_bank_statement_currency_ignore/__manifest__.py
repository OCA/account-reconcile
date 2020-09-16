# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Accounting: Ignore Bank Statement Currency",
    "summary": "Ignore amount in transaction currency on operations.",
    "version": "12.0.1.0.0",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-reconcile",
    "author": "CorporateHub, Odoo Community Association (OCA)",
    "maintainers": ["alexey-pelykh"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
    "depends": [
        "account",
    ],
    "data": [
        "templates/assets.xml",
        "views/account_bank_statement_line.xml",
        "views/account_bank_statement.xml",
    ],
    "qweb": [
        "static/src/xml/account_reconciliation.xml",
    ],
}
