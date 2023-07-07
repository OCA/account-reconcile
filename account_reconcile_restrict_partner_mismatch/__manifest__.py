# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Reconcile restrict partner mismatch",
    "summary": "Restrict reconciliation on receivable "
    "and payable accounts to the same partner",
    "version": "15.0.1.0.0",
    "depends": ["account"],
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "category": "Finance",
    "license": "AGPL-3",
    "data": ["report/account_move_lines_report.xml", "security/ir.model.access.csv"],
    "installable": True,
}
