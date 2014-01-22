# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Author: Leonardo Pistone                                                  #
#   Copyright 2014 Camptocamp SA                                              #
#                                                                             #
#   Inspired by module account_banking by EduSense BV, Therp BV, Smile        #
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
{
    'name': "Account Statement Cancel Line",
    'version': '0.1',
    'author': 'Camptocamp',
    'maintainer': 'Camptocamp',
    'category': 'Finance',
    'complexity': 'normal',
    'depends': [
        'account',
        'account_statement_ext',
        'account_default_draft_move',
    ],
    'description': """
        Account Statement Cancel Line

        This module allows to cancel one line of the statement without
        cancelling the whole thing.
    """,
    'website': 'http://www.camptocamp.com',
    'init_xml': [],
    'update_xml': [
        'statement_view.xml',
    ],
    'demo_xml': [],
    'test': [
    ],
    'installable': True,
    'images': [],
    'license': 'AGPL-3',
}
