# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume
#    Copyright 2011-2012 Camptocamp SA
#    Copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>)
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
    'name': "Bank statement import - commissions",
    'version': '1.0',
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'maintainer': 'Camptocamp',
    'category': 'Finance',
    'complexity': 'normal',
    'depends': [
        'account_statement_base_import'
    ],
    'description': """
This module brings commission support to bank statement imports. It computes
the sum of a commission field on each transaction and creates a statement
entry for it.
""",
    'website': 'http://www.camptocamp.com',
    'data': [
        "statement_view.xml",
        "import_statement_view.xml",
    ],
    'test': [],
    'installable': False,
    'images': [],
    'auto_install': False,
    'license': 'AGPL-3',
}
