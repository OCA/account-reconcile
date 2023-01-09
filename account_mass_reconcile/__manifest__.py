# Copyright 2012-2016 Camptocamp SA
# Copyright 2010 Sébastien Beau
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Mass Reconcile",
    "version": "15.0.1.0.0",
    "depends": ["account"],
    "author": "Akretion,Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-reconcile",
    "category": "Finance",
    "data": [
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "views/mass_reconcile.xml",
        "views/mass_reconcile_history_view.xml",
        "views/res_config_view.xml",
    ],
    "license": "AGPL-3",
}
