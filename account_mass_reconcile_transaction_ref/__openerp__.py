# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    'name': 'Mass Reconcile Transaction Ref',
    'version': '9.0.1.0.0',
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'category': 'Finance',
    'website': 'http://www.camptocamp.com',
    'license': 'AGPL-3',
    'depends': [
        'account_mass_reconcile',
        'base_transaction_id'
    ],
    'data': [
        'views/mass_reconcile_view.xml'
    ],
    'demo': [],
    'test': [],
    'auto_install': False,
    'installable': True,
    'images': []
}
