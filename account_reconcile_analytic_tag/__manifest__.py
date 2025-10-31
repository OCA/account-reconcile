# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Analytic tags in account reconciliation",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "version": "16.0.1.2.2",
    "depends": ["account_reconcile_oca", "account_analytic_tag"],
    "license": "AGPL-3",
    "category": "Accounting",
    "installable": True,
    "maintainers": ["victoralmau"],
    "data": [
        "views/account_bank_statement_line_views.xml",
        "views/account_reconcile_model_views.xml",
    ],
}
