# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher (Camptocamp)
#    Copyright 2012 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{'name': 'Base transaction id for financial institutes',
 'version': '8.0.1.0.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Hidden/Dependency',
 'complexity': 'easy',
 'depends': [
     'account',
     'stock_account',
     'sale_stock',
 ],
 'description': """
 Adds transaction id to invoice and sale models and views.
 On Sales order, you can specify the transaction ID used
 for the payment and it will be propagated to the invoice
 (even if made from packing).
 This is mostly used for e-commerce handling.
 You can then add a mapping on that SO field to save
 the e-commerce financial Transaction ID into the
 OpenERP sale order field.
 The main purpose is to ease the reconciliation process and
 be able to find the partner when importing the bank statement.
 """,
 'website': 'http://www.openerp.com',
 'data': [
     'invoice_view.xml',
     'sale_view.xml',
     'account_move_line_view.xml',
     'views/base_transaction_id.xml',
 ],
 'test': [],
 'installable': True,
 'images': [],
 'auto_install': False,
 'license': 'AGPL-3',
 }
