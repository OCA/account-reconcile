# Copyright 2020 Ozono Multimedia - Iván Antón
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "account_reconciliation_widget",
    "version": "14.0.1.3.2",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Account reconciliation widget",
    "author": "Odoo, Ozono Multimedia, Odoo Community Association (OCA)",
    "development_status": "Mature",
    "website": "https://github.com/OCA/account-reconcile",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/res_config_settings_views.xml",
        "views/assets.xml",
        "views/account_view.xml",
        "views/account_bank_statement_view.xml",
        "views/account_journal_dashboard_view.xml",
    ],
    "qweb": [
        "static/src/xml/account_reconciliation.xml",
    ],
    "installable": True,
}
