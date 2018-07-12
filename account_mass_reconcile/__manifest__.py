# -*- coding: utf-8 -*-
# © 2012-2016 Camptocamp SA (Guewen Baconnier, Damien Crier, Matthieu Dietrich)
# © 2010 Sébastien Beau
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Mass Reconcile",
    "version": "10.0.1.0.0",
    "depends": ["account"],
    "author": "Akretion,Camptocamp,Odoo Community Association (OCA)",
    "website": "http://www.akretion.com/",
    "category": "Finance",
    "data": ["views/mass_reconcile.xml",
             "views/mass_reconcile_history_view.xml",
             "security/ir_rule.xml",
             "security/ir.model.access.csv",
             "views/res_config_view.xml",
             ],
    'license': 'AGPL-3',
    "auto_install": False,
    'installable': True,

}
