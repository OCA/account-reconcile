# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Laurent Mignon
#    Copyright 2013 'ACSONE SA/NV'
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

{'name': "Bank statement CODA import",
 'version': '1.0',
 'author': 'Laurent Mignon (Acsone)',
 'maintainer': 'ACSONE SA/NV',
 'category': 'Finance',
 'complexity': 'normal',
 'depends': [
     'account_statement_base_import',
     'account_statement_bankaccount_completion'
     ],
 'description': """
 This module brings generic methods and fields on bank statement to deal with
 the importation of coded statement of account from electronic files.

 This module allows you to import your bank transactions with a standard CODA file
 (you'll find samples in the 'data' folder). It respects the chosen profile
 (model provided by the account_statement_ext module) to generate the entries.

 """,
 'website': 'http://www.acsone.eu',
 'external_dependencies': {
     'python' : ['coda'],
 },
 'init_xml': [],
 'update_xml': [
 ],
 'demo_xml': [],
 'test': [],
 'installable': True,
 'images': [],
 'auto_install': False,
 'license': 'AGPL-3',
}
