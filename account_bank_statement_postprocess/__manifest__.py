# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Accounting: Bank Statement Post-processing",
    "summary": "Process imported bank statements to enrich records.",
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
        "security/account_bank_statement_postprocess.xml",
        "security/ir.model.access.csv",
        "views/account_bank_statement_line.xml",
        "views/account_bank_statement_postprocess_model.xml",
        "views/account_bank_statement.xml",
    ],
}
