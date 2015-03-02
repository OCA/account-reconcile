# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi, Joel Grand-Guillaume
#    Copyright 2011-2013 Camptocamp SA
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
 'version': '1.3.6',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Finance',
 'complexity': 'normal',
 'depends': ['account',
             'report_webkit',
             'account_voucher'],
 'description': """
 Improve the basic bank statement, by adding various new features, and help
 dealing with huge volume of reconciliation through payment offices such as
 Paypal, Lazer, Visa, Amazon...

 It is mostly used for E-commerce but can be useful for other use cases as it
 introduces a notion of profile on the bank statement to have more control on
 the generated entries. It serves as a base for all new features developped to
 improve the reconciliation process (see our other set of modules:

 * account_statement_base_completion
 * account_statement_base_import
 * account_advanced_reconcile

 Features:

 1) Improve the bank statement: allows to  define profiles (for each Office or
 Bank). The bank statement will then generate the entries based on some
 criteria chosen in the selected profile. You can setup on the profile:

  - the journal to use
  - use balance check or not
  - account commission and Analytic account for commission
  - partner concerned by the profile (used in commission and optionaly on
    generated credit move)
  - use a specific credit account (instead of the receivalble/payable default
    one)
  - force Partner on the counter-part move (e.g. 100.- debit, Partner: M.
    Martin; 100.- credit, Partner: HSBC)

 2) Add a report on bank statement that can be used for checks remittance

 3) When an error occurs in a bank statement confirmation, go through all line
    anyway and summarize all the erronous line in a same popup instead of
    raising and crashing on every step.

 4) Remove the period on the bank statement, and compute it for each line based
    on their date instead. It also adds this feature in the voucher in order to
    compute the period correctly.

 5) Cancelling a bank statement is much more easy and will cancel all related
 entries, unreconcile them, and finally delete them.

 6) Add the ID in entries view so that you can easily filter on a statement ID
    to reconcile all related entries at once (e.g. one statement (ID 100) for
    Paypal on an intermediate account, and then another for the bank on the
    bank account. You can then manually reconcile all the line from the first
    one with one line of the second by finding them through the statement ID.)
 """,
 'website': 'http://www.camptocamp.com',
 'data': ['statement_view.xml',
          'account_view.xml',
          'report/bank_statement_webkit_header.xml',
          'report.xml',
          'security/ir.model.access.csv',
          'security/ir_rule.xml'],
 'demo_xml': [],
 'test': ['test/test_profile_related_fields.yml'],
 'installable': False,
 'images': [],
 'auto_install': False,
 'license': 'AGPL-3',
 'active': False,
 }
