# -*- coding: utf-8 -*-
# © 2012 Yannick Vaucher, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{'name': 'Base transaction id for financial institutes',
 'version': '10.0.1.1.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Hidden/Dependency',
 'depends': [
     'sale',
     'account',
 ],
 'website': 'https://www.odoo-community.org/',
 'data': [
     'views/account_payment.xml',
     'views/invoice.xml',
     'views/sale.xml',
     'views/account_move_line.xml',
     'views/base_transaction_id.xml',
 ],
 'installable': True,
 'license': 'AGPL-3',
 }
