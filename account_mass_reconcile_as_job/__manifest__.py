# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    'name': 'Account Mass Reconcile as Jobs',
    'version': '12.0.0.1.0',
    'category': 'Accounting',
    'depends': [
        'queue_job',
        'account_mass_reconcile',
    ],
    'author': 'Camptocamp, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/account-reconcile',
    'data': [
        'data/ir_config_parameter.xml',
    ],
    'installable': True,
    'application': False,
}
