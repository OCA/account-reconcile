# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Reconcile Payment Order",
    "summary": """
        Allow to reconcile payment order on reconcile widget""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "depends": ["account_reconcile_oca", "account_payment_order"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/account_payment_order_maturity.xml",
        "views/account_bank_statement_line.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "account_reconcile_payment_order/static/src/**/*.esm.js",
            "account_reconcile_payment_order/static/src/**/*.xml",
        ]
    },
    "post_init_hook": "post_init_hook",
    "demo": [],
}
