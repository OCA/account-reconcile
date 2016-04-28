# -*- coding: utf-8 -*# -*- coding: utf-8 -*-
# © 2012 Yannick Vaucher (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{'name': 'Base transaction id for financial institutes',
 'version': '9.0.1.0.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Hidden/Dependency',
 'complexity': 'easy',
 'depends': [
     'account',
     'stock_account',
     'sale_stock',
 ],
 'website': 'http://www.openerp.com',
 'data': [
     'views/invoice.xml',
     'views/sale.xml',
     'views/account_move_line.xml',
     'views/base_transaction_id.xml',
 ],
 'test': [],
 'installable': True,
 'images': [],
 'auto_install': False,
 'license': 'AGPL-3',
 }
