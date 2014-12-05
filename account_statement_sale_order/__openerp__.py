# -*- encoding: utf-8 -*-
##############################################################################
#
#    account_statement_sale_order for OpenERP
#    Copyright (C) 2013-14 Akretion Chafique DELLI <chafique.delli@akretion.com>
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
    'name': 'Bank Statement Sale Order',
    'version': '0.1',
    'category': 'Finance',
    'license': 'AGPL-3',
    'summary': '',
    'description': """
    The goal of this module is to create a self-completion method fill:
    command, partner and receivable account of a bank statement line.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['sale'],
    'data': ['statement_view.xml'],
    'installable': True,
}
