# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Reconciliation Date",
    "summary": "Track Reconciliation Date of Payments and Invoices",
    "version": "12.0.1.1.0",
    "depends": ["account"],
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "http://www.github.com/OCA/account-reconcile",
    "category": "Finance",
    'license': 'AGPL-3',
    "data": [
        'views/account_invoice.xml',
        'views/account_payment.xml'
    ],
    'installable': True,
}
