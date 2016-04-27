# -*- coding: utf-8 -*-
# © 2011-2016 Camptocamp SA
#             Joel Grand-Guillaume, Nicolas Bessi, Matthieu Dietrich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Bank statement base import",
    'version': '9.0.1.0.0',
    'author': "Akretion,Camptocamp,Odoo Community Association (OCA)",
    'category': 'Finance',
    'depends': ['account'],
    'website': 'http://www.camptocamp.com',
    'data': [
        "security/ir.model.access.csv",
        "data/completion_rule_data.xml",
        "wizard/import_statement_view.xml",
        "views/account_move_view.xml",
        "views/journal_view.xml",
        "views/partner_view.xml",
    ],
    'test': [
        'test/partner.yml',
        'test/invoice.yml',
        'test/supplier_invoice.yml',
        'test/refund.yml',
        'test/completion_test.yml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
