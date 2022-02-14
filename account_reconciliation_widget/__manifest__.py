# Copyright 2020 Ozono Multimedia - Iván Antón
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "account_reconciliation_widget",
    "version": "15.0.1.1.2",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Account reconciliation widget",
    "author": "Odoo, Ozono Multimedia, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_view.xml",
        "views/account_bank_statement_view.xml",
        "views/account_journal_dashboard_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "account_reconciliation_widget/static/src/scss/account_reconciliation.scss",
            "account_reconciliation_widget/static/src/js/reconciliation/**/*",
        ],
        "web.qunit_suite_tests": [
            "account_reconciliation_widget/static/tests/**/*",
        ],
        "web.assets_qweb": [
            "account_reconciliation_widget/static/src/xml/account_reconciliation.xml",
        ],
    },
    "installable": True,
}
