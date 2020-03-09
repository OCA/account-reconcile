# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Reconciliation Widget Partial',
    'summary': """
        Allow to modifiy the reconcile amount for partial payments""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-reconcile',
    'depends': [
        'account',
    ],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/account_reconciliation.xml',
    ],
}
