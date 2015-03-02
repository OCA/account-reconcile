# -*- coding: utf-8 -*-
###############################################################################
#
#   account_statement_one_move for OpenERP
#   Copyright (C) 2013-TODAY Akretion <http://www.akretion.com>.
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'Bank statement one move',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """
    This module allows to group all lines of a bank statement in only one move.
    This feature is optional and can be activated with a checkbox in the bank
    statement's profile. This is very useful for credit card deposit for
    example, you won't have a move for each line.

    """,
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['account_statement_ext'],
    'data': [
        'statement_view.xml'
    ],
    'demo': [],
    'installable': False,
    'auto_install': False,
    'active': False,
}
