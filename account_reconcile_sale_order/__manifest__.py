# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Reconcile sales orders",
    "summary": "Invoice and reconcile sales orders",
    "version": "18.0.1.0.1",
    "development_status": "Alpha",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-reconcile",
    "author": "Hunki Enterprises BV, Odoo Community Association (OCA)",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "depends": [
        "sale",
        "account_reconcile_oca",
    ],
    "data": [
        "views/account_bank_statement_line.xml",
        "views/account_reconcile_model.xml",
        "views/sale_order.xml",
    ],
    "demo": [
        "demo/account_reconcile_model.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/account_reconcile_sale_order/static/src/js/account_reconcile_sale_order.*",
        ],
    },
}
