# Copyright 2017-2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    'name': 'Account Mass Reconcile as Jobs',
    'version': '12.0.0.1.0',
    'category': 'Accounting',
    'depends': [
        'connector',
        'account_mass_reconcile',
        #  TODO: not yet migrated to 12.0
        'account_mass_reconcile_transaction_ref',
        #  TODO: not yet migrated to 12.0
        'account_mass_reconcile_ref_deep_search',
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
