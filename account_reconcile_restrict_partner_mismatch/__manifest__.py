# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Reconcile restrict partner mismatch",
    "summary": "Restrict reconciliation on receivable "
    "and payable accounts to the same partner",
    "version": "16.0.1.0.0",
    "depends": ["account"],
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "category": "Finance",
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "report/account_move_lines_report.xml",
        "views/account_journal.xml",
        "views/res_config_settings.xml",
    ],
    "installable": True,
}
