# -*- coding: utf-8 -*-
# © 2013 ACSONE SA/NV
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    'name': "Journal Entry completion from bank account number",
    'version': '9.0.1.0.0',
    'author': "ACSONE SA/NV,Odoo Community Association (OCA)",
    'maintainer': 'ACSONE SA/NV',
    'category': 'Finance',
    'complexity': 'normal',
    'depends': [
        'account_move_base_import',
    ],
    'website': 'http://www.acsone.eu',
    'data': [
        "data/completion_rule_data.xml",
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
