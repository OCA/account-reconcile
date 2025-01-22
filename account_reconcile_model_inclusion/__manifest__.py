# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Reconciliation model inclusion/exclusion",
    "summary": "Allows to match only when other models match/don't match",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-reconcile",
    "author": "Hunki Enterprises BV, Odoo Community Association (OCA)",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "views/account_reconcile_model.xml",
    ],
    "demo": [
        "demo/account_reconcile_model.xml",
    ],
}
