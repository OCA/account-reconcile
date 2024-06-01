# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Reconcile sale orders",
    "summary": "Invoice and reconcile sale orders",
    "version": "15.0.1.0.0",
    "development_status": "Alpha",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-reconcile",
    "author": "Hunki Enterprises BV, Odoo Community Association (OCA)",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "depends": [
        "sale",
        "account_reconciliation_widget",
    ],
    "data": [
        "views/account_reconcile_model.xml",
    ],
    "demo": [
        "demo/account_reconcile_model.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "account_reconcile_sale_order/static/src/js/*.js",
        ],
    },
}
