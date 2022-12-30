# Copyright 2015-2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    "name": "Mass Reconcile Ref Deep Search",
    "version": "14.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "category": "Finance",
    "website": "https://github.com/OCA/account-reconcile",
    "license": "AGPL-3",
    "depends": ["account_mass_reconcile"],
    "data": [
        "views/mass_reconcile_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
