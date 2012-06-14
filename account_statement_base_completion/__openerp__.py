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

{'name': "Bank statement base completion",
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Finance',
 'complexity': 'normal', #easy, normal, expert
 'depends': ['account_statement_ext'],
 'description': """
 The goal of this module is to improve the basic bank statement, help dealing with huge volume of
 reconciliation by providing basic rules to identify the partner of a bank statement line.
 It will also take care of the chosen profile to make his work.
 
 His goal is to provide an easy way to fullfill the info of a bank statement line based on rules.
 The reference of the line is always used by the reconciliation process. We're supposed to copy 
 there (or write manually) the matching string. That can be : the order Number or an invoice number, 
 or anything that will be found in the invoice entry part to make the match.
 
 """,
 'website': 'http://www.camptocamp.com',
 'init_xml': [],
 'update_xml': [
     'statement_view.xml',
     'data.xml',
 ],
 'demo_xml': [],
 'test': [],
 'installable': True,
 'images': [],
 'auto_install': False,
 'license': 'AGPL-3',
 'active': False,
}
