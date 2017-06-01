# -*- coding: utf-8 -*-
# © 2015-2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Bank statement link partner',
    'version': '8.0.0.5.1',
    'license': 'AGPL-3',
    'author': 'Therp BV,Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/bank-statement-reconcile',
    'category': 'Banking addons',
    'depends': [
        'account',
        ],
    'data': [
        'view/account_bank_statement.xml',
        'wizard/link_partner.xml',
    ],
    'installable': True,
    'auto_install': False,
}
