# -*- coding: utf-8 -*-
# Author: Guewen Baconnier
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{'name': 'Bank Statement Operation Rules',
 'version': '9.0.1.0.0',
 'author': 'Camptocamp, Odoo Community Association (OCA)',
 'maintainer': 'Odoo Community Association (OCA)',
 'license': 'AGPL-3',
 'category': 'Accounting & Finance',
 'depends': [
     'account',
 ],
 'website': 'http://www.camptocamp.com',
 'data': [
     'view/account_operation_rule.xml',
     'view/account_operation_rule_view.xml',
     'security/ir.model.access.csv',
 ],
 'installable': True,
 'auto_install': False,
 }
