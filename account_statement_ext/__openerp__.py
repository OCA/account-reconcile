# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi, Joel Grand-Guillaume
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

{'name': "Bank statement extension and profiles",
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Finance',
 'complexity': 'normal', #easy, normal, expert
 'depends': ['base_transaction_id'],
 'description': """
 The goal of this module is to help dealing with huge volume of reconciliation through
 payment offices like Paypal, Lazer, Visa, Amazon and so on. It's mostly used for
 E-commerce but can be usefule for other use cases as it introduce a notion of profil
 on the bank statement to have more control on the generated entries.
 
 Features:
 
 1) This module improves the bank statement that allow and you to import your bank transactions with
 a standard .csv or .xls file (you'll find it in the 'data' folder). You can now define profile for each
 Office or Bank that will generate the entries based on some criteria. You can setup:
 
  - Account commission and partner relation
  - Can force an account for the reconciliation
  - Choose to use balance check or not
  - Analytic account for commission
  - Force Partner on the counter-part move (e.g. 100.- debit, Partner: M.Martin; 100.- credit, Partner: HSBC)
 
 2) Adds a report on bank statement that can be used for Checks
 
 3) When an error occurs in a bank statement confirmation, it will go through all line anyway and summarize 
 all the erronous line in a same popup instead of raising and crashing on every step.
 
 4) Remove the period on the bank statement, and compute it for each line based on their date instead. 
 
 5) Provide a standard import format to create and fullfill a bank statement from a .csv or .xls file. For
 

 """,
 'website': 'http://www.camptocamp.com',
 'init_xml': [],
 'update_xml': [
     'statement_view.xml',
     'wizard/import_statement_view.xml',
     'report/bank_statement_webkit_header.xml',
     'report.xml',
 ],
 'demo_xml': [],
 'test': [],
 'installable': True,
 'images': [],
 'auto_install': False,
 'license': 'AGPL-3',
 'active': False,
}
