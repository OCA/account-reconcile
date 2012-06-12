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

{'name': "Bank statement easy import",
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Finance',
 'complexity': 'normal', #easy, normal, expert
 'depends': ['account_statement_ext','account_statement_base_completion'],
 'description': """
 The goal of this module is bring basic method and fields on bank statement to deal with 
 the importation of different bank and offices.
 
 
 """,
 'website': 'http://www.camptocamp.com',
 'init_xml': [],
 'update_xml': [
 ],
 'demo_xml': [],
 'test': [],
 'installable': True,
 'images': [],
 'auto_install': False,
 'license': 'AGPL-3',
 'active': False,
}
