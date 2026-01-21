# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Reconcile OCA - Add default filters",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Add default filters in Reconcile tab when the bank statement line "
    "has a partner",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/account-reconcile",
    "depends": ["account_reconcile_oca", "base_view_inheritance_extension"],
    "data": [
        "views/account_move_line.xml",
        "views/account_bank_statement_line.xml",
    ],
    "installable": True,
}
