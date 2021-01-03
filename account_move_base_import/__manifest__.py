# Copyright 2011-2016 Akretion
# Copyright 2011-2019 Camptocamp SA
# Copyright 2013 Savoir-faire Linux
# Copyright 2014 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    "name": "Journal Entry base import",
    "version": "14.0.1.0.0",
    "author": "Akretion,Camptocamp,Odoo Community Association (OCA)",
    "category": "Finance",
    "depends": ["account"],
    "website": "https://github.com/OCA/account-reconcile",
    "data": [
        "security/ir.model.access.csv",
        "data/completion_rule_data.xml",
        "wizard/import_statement_view.xml",
        "views/account_move_view.xml",
        "views/journal_view.xml",
        "views/partner_view.xml",
    ],
    "external_dependencies": {"python": ["xlrd"]},
    "installable": True,
    "license": "AGPL-3",
}
