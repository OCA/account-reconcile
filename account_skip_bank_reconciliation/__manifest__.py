# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Skip Bank Reconciliation",
    "summary": "Allows to exclude from bank statement reconciliation "
    "all journal items of a reconcilable account",
    "version": "13.0.1.0.0",
    "depends": ["account"],
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://www.github.com/OCA/account-reconcile",
    "category": "Finance",
    "data": ["views/account_view.xml", "views/account_journal_view.xml"],
    "license": "AGPL-3",
    "installable": True,
}
