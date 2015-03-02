# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume
#    Copyright 2011-2012 Camptocamp SA
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

{'name': "Bank statement completion from transaction ID",
 'version': '1.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Finance',
 'complexity': 'normal',
 'depends': [
     'account_statement_base_completion',
     'base_transaction_id'
 ],
 'description': """
  Add a completion method based on transaction ID providen by the bank/office.

  This transaction ID has been recorded on the SO (by a mapping
  through the e-commerce connector, or manually). Completion will look
  in the SO with that transaction ID to match the partner, then it
  will fill in the bank statement line with it,  as well as
  the reference with the found SO name to ease the reconciliation.

  This way, the reconciliation always happen on the SO name stored in ref.

 """,
 'website': 'http://www.camptocamp.com',
 'init_xml': [],
 'update_xml': [
     "statement_view.xml",
     "data.xml",
 ],
 'demo_xml': [],
 'test': [
     'test/sale.yml',
     'test/completion_transactionid_test.yml',
     'test/invoice.yml',
     'test/completion_invoice_transactionid_test.yml',
 ],
 'installable': False,
 'images': [],
 'auto_install': True,
 'license': 'AGPL-3',
 }
