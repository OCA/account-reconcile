# Author: Guewen Baconnier
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{'name': 'Account Reconcile Rules',
 'version': '11.0.1.0.0',
 'author': 'Camptocamp, Odoo Community Association (OCA)',
 'maintainer': 'Odoo Community Association (OCA)',
 'license': 'AGPL-3',
 'category': 'Accounting & Finance',
 'depends': [
     'account',
 ],
 'website': 'https://github.com/OCA/account-reconcile',
 'data': [
     'views/account_reconcile_rule.xml',
     'views/account_reconcile_rule_view.xml',
     'security/ir.model.access.csv',
 ],
 }
