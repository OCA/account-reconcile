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
    'name': "Bank statement transactionID import",
    'version': '1.0',
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'maintainer': 'Camptocamp',
    'category': 'Finance',
    'complexity': 'normal',
    'depends': [
        'account_statement_base_import',
        'account_statement_transactionid_completion'
    ],
    'description': """
 This module brings generic methods and fields on bank statement to deal with
 the importation of different bank and offices that uses transactionID.

 This module allows you to import your bank transactions with a standard .csv
 or .xls file (you'll find samples in the 'data' folder). It respects the
 chosen profile (model provided by the account_statement_ext module) to
 generate the entries.

 This module can handle a commission taken by the payment office and has the
 following format:

 * transaction_id: the transaction ID given by the bank/office. It is used as
   reference in the generated entries and is useful for reconciliation process
 * date: date of the payment
 * amount: amount paid in the currency of the journal used in the importation
   profile
 * commission_amount: amount of the comission for each line
 * label: the comunication given by the payment office, used as communication
   in the generated entries.
    """,
    'website': 'http://www.camptocamp.com',
    'installable': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
