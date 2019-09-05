# -*- coding: utf-8 -*-
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Exclude From Bank Statement Reconciliation',
    'summary': "Adds a flag to accounts that prevents them from being "
               "proposed during bank statement reconciliation",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Eficent Business and IT Consulting Services S.L.,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-reconcile',
    'depends': [
        "account_bank_reconcile_hook"
    ],
    'data': [
        'views/account_view.xml',
    ],
}
