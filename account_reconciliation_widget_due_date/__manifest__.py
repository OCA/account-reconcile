# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Reconciliation Widget Due Date",
    "version": "15.0.1.0.1",
    "website": "https://github.com/OCA/account-reconcile",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account_reconciliation_widget"],
    "maintainers": ["victoralmau"],
    "development_status": "Production/Stable",
    "data": ["views/account_bank_statement_line_view.xml"],
    "assets": {
        "web.assets_backend": [
            "/account_reconciliation_widget_due_date/static/src/js/*",
        ],
    },
}
