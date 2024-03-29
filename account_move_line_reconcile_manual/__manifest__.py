# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Move Line Reconcile Manual",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Manually reconcile Journal Items",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/account-reconcile",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/account_move_line_reconcile_manual_view.xml",
        "views/account_move_line.xml",
    ],
    "installable": True,
}
