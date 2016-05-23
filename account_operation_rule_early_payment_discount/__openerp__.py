# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Early Payment Discount Reconciliation Rules',
    'version': '9.0.1.0.0',
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'category': 'Accounting & Finance',
    'depends': [
        'account_operation_rule',
        'account_early_payment_discount',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'view/account_operation_rule_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
