# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Reconcile Oca",
    "summary": """
        Reconcile addons for Odoo CE accounting""",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca,Dixmit,Odoo Community Association (OCA)",
    "maintainers": ["etobella"],
    "website": "https://github.com/OCA/account-reconcile",
    "depends": [
        "account_statement_base",
    ],
    "data": [
        "views/res_config_settings.xml",
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/account_account_reconcile.xml",
        "views/account_bank_statement_line.xml",
        "views/account_move_line.xml",
        "views/account_journal.xml",
        "views/account_move.xml",
        "views/account_account.xml",
        "views/account_bank_statement.xml",
        "views/account_reconcile_model.xml",
    ],
    "demo": ["demo/demo.xml"],
    "post_init_hook": "post_init_hook",
    "assets": {
        "web.assets_backend": [
            "account_reconcile_oca/static/src/components/**/*.esm.js",
            "account_reconcile_oca/static/src/components/**/*.xml",
            "account_reconcile_oca/static/src/components/**/*.scss",
            "account_reconcile_oca/static/src/views/**/*.esm.js",
            "account_reconcile_oca/static/src/views/**/*.xml",
            "account_reconcile_oca/static/src/views/**/*.scss",
            "account_reconcile_oca/static/src/scss/reconcile.scss",
        ],
        "web.assets_unit_tests": [
            "account_reconcile_oca/static/tests/**/*.test.js",
        ],
    },
}
