# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Account Mass Reconcile Scheduled",
    "summary": "Schedule only selected mass reconcile records",
    "version": "10.0.1.0.0",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-reconcile",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "account_mass_reconcile",
    ],
    "data": [
        "data/ir_cron.xml",
        "views/account_mass_reconcile.xml",
    ],
    "application": False,
    "installable": True,
}
