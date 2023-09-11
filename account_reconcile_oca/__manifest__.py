# Copyright 2022 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Reconcile Oca",
    "summary": """
        Reconcile addons for Odoo CE accounting""",
    "version": "16.0.1.2.2",
    "license": "AGPL-3",
    "author": "CreuBlanca,Odoo Community Association (OCA)",
    "maintainers": ["etobella"],
    "website": "https://github.com/OCA/account-reconcile",
    "depends": [
        "account_statement_base",
        "base_sparse_field",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_account_reconcile.xml",
        "views/account_bank_statement_line.xml",
        "views/account_move_line.xml",
        "views/account_journal.xml",
        "views/account_move.xml",
        "views/account_account.xml",
    ],
    "demo": ["demo/demo.xml"],
    "post_init_hook": "post_init_hook",
    "assets": {
        "web.assets_backend": [
            "account_reconcile_oca/static/src/js/widgets/reconcile_data_widget.esm.js",
            "account_reconcile_oca/static/src/js/widgets/reconcile_chatter_field.esm.js",
            "account_reconcile_oca/static/src/js/widgets/selection_badge_uncheck.esm.js",
            "account_reconcile_oca/static/src/js/widgets/reconcile_move_line_widget.esm.js",
            "account_reconcile_oca/static/src/js/reconcile_move_line/*.esm.js",
            "account_reconcile_oca/static/src/js/reconcile_form/*.esm.js",
            "account_reconcile_oca/static/src/js/reconcile_manual/*.esm.js",
            "account_reconcile_oca/static/src/js/reconcile/*.esm.js",
            "account_reconcile_oca/static/src/xml/reconcile.xml",
            "account_reconcile_oca/static/src/scss/reconcile.scss",
        ],
    },
}
