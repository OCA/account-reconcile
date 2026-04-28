# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Reconcile from Wizard",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Tecnativa,Odoo Community Association (OCA)",
    "maintainers": ["carlos-lopez-tecnativa"],
    "website": "https://github.com/OCA/account-reconcile",
    "depends": ["account_reconcile_oca"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/account_manual_reconcile_wizard.xml",
        "views/account_move_line.xml",
    ],
}
