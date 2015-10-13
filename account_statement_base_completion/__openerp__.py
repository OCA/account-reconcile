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

{
    'name': "Bank statement base completion",
    'version': '1.0.3',
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'maintainer': 'Camptocamp',
    'category': 'Finance',
    'complexity': 'normal',
    'depends': ['account_statement_ext',
                'account_report_company'],
    'description': """
 The goal of this module is to improve the basic bank statement, help dealing
 with huge volume of reconciliation by providing basic rules to identify the
 partner of a bank statement line.
 Each bank statement profile can have its own rules to be applied according to
 a sequence order.

 Some basic rules are provided in this module:

 1) Match from statement line label (based on partner field 'Bank Statement
    Label')
 2) Match from statement line label (based on partner name)
 3) Match from statement line reference (based on Invoice number)

 You can easily override this module and add your own rules in your own one.
 The basic rules only fill in  the partner, but you can use them to fill in
 any value of the line (in the future, we will add a rule to automatically
 match and reconcile the line).

 It adds as well a label on the bank statement line (on which the pre-define
 rules can match) and a char field on the partner called 'Bank Statement
 Label'.  Using the pre-define rules, you will be able to match various
 labels for a partner.

 The reference of the line is always used by the reconciliation process. We're
 supposed to copy there (or write manually) the matching string. This can be:
 the order Number or an invoice number, or anything that will be found in the
 invoice accounting entry part to make the match.

 You can use it with  our account_advanced_reconcile module to automatize the
 reconciliation process.


 TODO: The rules that look for invoices to find out the partner should take
 back the payable / receivable account from there directly instead of
 retrieving it from partner properties!
    """,
    'website': 'http://www.camptocamp.com',
    'data': [
        'statement_view.xml',
        'partner_view.xml',
        'data.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [
        'test/partner.yml',
        'test/invoice.yml',
        'test/supplier_invoice.yml',
        'test/refund.yml',
        'test/completion_test.yml'
    ],
    'installable': False,
    'images': [],
    'auto_install': False,
    'license': 'AGPL-3',
}
