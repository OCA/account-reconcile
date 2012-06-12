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
 The goal of this module is to improve the basic bank statement, help dealing with huge volume of
 reconciliation through payment offices like Paypal, Lazer, Visa, Amazon and so on. 
 
 It will be mostly used for E-commerce but can be usefule for other use cases as it introduce a 
 notion of profil on the bank statement to have more control on the generated entries. It will
 be the base for all new features developped to improve the reconciliation process. 
 
 Features:
 
 1) This module improves the bank statement that allow and you to define profile for each
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
 
 5) Cancelling a bank statement is much more easy and will cancel all related entries, unreconcile them,
    and finally delete it. 
 
 6) Add the ID in entries view so that you can easily filter on a statement ID to reconcile all related 
    entries at once (e.g. one statement (ID 100) for paypal on an intermediate account, and then another for
    the bank on the bank account. You can then manually reconcile all the line from the first one with
    one line of the second by finding them through the statement ID.)
 
 """,
 'website': 'http://www.camptocamp.com',
 'init_xml': [],
 'update_xml': [
     'statement_view.xml',
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
