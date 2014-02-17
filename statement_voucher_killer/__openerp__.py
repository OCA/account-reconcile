# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2013 Camptocamp SA (http://www.camptocamp.com)
#   @author Nicolas Bessi
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

{'name': 'Satement voucher killer',
 'version': '1.0.0',
 'category': 'other',
 'description': """
Prevent voucher creation when importing lines into statement.
#############################################################

When importing invoice or payment into a bank statement or a payment order, normally a
draft voucher is created on the line. This module will disable this voucher creation.
When importing payment line, date used to populate statement
line will be take from imported line in this order:

 * Date
 * Maturity date
 * Related statement date

""",
 'author': 'Camptocamp',
 'website': 'http://www.camptocamp.com',
 'depends': ['account_voucher', 'account_payment'],
 'data': [
     'statement_view.xml',
     ],
 'test': [],
 'installable': True,
 'active': False,
 }
