# Copyright 2022 Ecosoft Co., Ltd (http://ecosoft.co.th/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Reconciliation Widget with Check Number",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "depends": [
        "account_reconciliation_widget",
        "bank_statement_check_number",
    ],
    "data": [
        "views/assets.xml",
    ],
    "qweb": [
        "static/src/xml/account_reconciliation.xml",
    ],
    "installable": True,
}
