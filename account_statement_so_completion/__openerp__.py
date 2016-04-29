# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Author: Joel Grand-Guillaume
#   Copyright 2011-2012 Camptocamp SA
#                                                                             #
#   Author: Leonardo Pistone <leonardo.pistone@camptocamp.com>                #
#   Copyright 2013 Camptocamp SA                                              #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

{'name': "Bank statement Sale Order completion",
 'version': '9.0.1.0.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Finance',
 'complexity': 'easy',
 'depends': ['account_statement_base_import', 'sale'],
 'website': 'http://www.camptocamp.com',
 'data': [
     'data/completion_rule_data.xml',
 ],
 'test': [
     'test/completion_so_test.yml'],
 'installable': True,
 'images': [],
 'auto_install': False,
 'license': 'AGPL-3',
 }
