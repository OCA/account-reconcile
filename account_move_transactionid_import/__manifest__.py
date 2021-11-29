# © 2011-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    'name': "Journal Entry transactionID import",
    'version': '12.0.3.0.0',
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'maintainer': 'Camptocamp',
    'category': 'Finance',
    'complexity': 'normal',
    'depends': [
        'account_move_base_import',
        'base_transaction_id'
    ],
    'data': [
        'data/completion_rule_data.xml'
    ],
    'website': 'http://www.camptocamp.com',
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
