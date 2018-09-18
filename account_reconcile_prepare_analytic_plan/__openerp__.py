# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Prepare analytic plans before reconciliation",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Banking addons",
    "summary":
    "Assign bank transactions to analytic plans before reconciliation",
    "depends": [
        'account_analytic_plans',
        'account_reconcile_prepare_account',
    ],
    "data": [
        "views/account_bank_statement.xml",
        "views/templates.xml",
    ],
    "installable": True,
    "auto": True,
}
