# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Statement Reconcile Status",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Show reconciliation status on bank statements",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "depends": ["account_statement_base"],
    "data": [
        "views/account_bank_statement_views.xml",
    ],
    "installable": True,
}
