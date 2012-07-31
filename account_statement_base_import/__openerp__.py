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

{'name': "Bank statement base import",
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Finance',
 'complexity': 'normal', #easy, normal, expert
 'depends': ['account_statement_ext','account_statement_base_completion'],
 'description': """
 This module brings basic methods and fields on bank statement to deal with
 the importation of different bank and offices. A generic abstract method is defined and an
 example that gives you a basic way of importing bank statement through a standard file is provided.

 This module improves the bank statement and allows you to import your bank transactions with
 a standard .csv or .xls file (you'll find it in the 'data' folder). It respects the profile
 (provided by the accouhnt_statement_ext module) to pass the entries. That means,
 you'll have to choose a file format for each profile.

 This module can handle a commission taken by the payment office and has the following format:

 * ref :               the SO number, INV number or any matching ref found. It'll be used as reference
                       in the generated entries and will be useful for reconciliation process
 * date :              date of the payment
 * amount :            amount paid in the currency of the journal used in the importation profil
 * commission_amount : amount of the comission for each line
 * label :             the comunication given by the payment office, used as communication in the
                       generated entries.

 The goal is here to populate the statement lines of a bank statement with the infos that the
 bank or office give you. Fell free to inherit from this module to add your own format.Then,
 if you need to complete data from there, add your own account_statement_*_completion module and implement
 the needed rules.

 """,
 'website': 'http://www.camptocamp.com',
 'init_xml': [],
 'update_xml': [
        "wizard/import_statement_view.xml",
        "statement_view.xml",
 ],
 'demo_xml': [],
 'test': [],
 'installable': True,
 'images': [],
 'auto_install': False,
 'license': 'AGPL-3',
 'active': False,
}
