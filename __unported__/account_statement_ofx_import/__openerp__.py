# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Pedro Manuel Baeza Romero
#    Copyright 2013 Servicios Tecnológicos Avanzados
#    Financed by AB Internet (http://www.abinternet.co.uk/)
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

{'name': "Bank statement OFX import",
    'version': '1.0.1',
    'author': "Servicios Tecnológicos Avanzados - Pedro M. Baeza,Odoo Community Association (OCA)",
    'maintainer': 'Pedro M. Baeza',
    'category': 'Finance',
    'complexity': 'normal',
    'depends': [
        'account_statement_base_import',
    ],
    'external_dependencies': {
        'python': ['ofxparse'],
    },
    'description': """
    Allows to import OFX (Open Financial Exchange) statement files, using
    *account_statement_base_import* generic inheritance mechanism to import
    statements.

    It requires ofxparse library to work.
    """,
    'website': 'http://www.serviciosbaeza.com',
    'data': [],
    'test': [],
    'installable': False,
    'images': [],
    'auto_install': False,
    'license': 'AGPL-3',
 }
