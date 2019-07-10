# Copyright 2011-2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    'name': "Journal Entry Sale Order completion",
    'version': '12.0.1.0.0',
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'maintainer': 'Camptocamp',
    'category': 'Finance',
    'complexity': 'easy',
    'depends': ['account_move_base_import', 'sale'],
    'website': 'http://www.camptocamp.com',
    'data': [
        'data/completion_rule_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
