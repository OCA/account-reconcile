# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Account Mass Reconcile as Cron Jobs",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "depends": [
        "queue_job",
        "account_mass_reconcile",
    ],
    "author": "ForgeFlow, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/account-reconcile",
    "data": [
        "data/ir_cron.xml",
        "views/mass_reconcile.xml",
    ],
    "installable": True,
    "application": False,
}
