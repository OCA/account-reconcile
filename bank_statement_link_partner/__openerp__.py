# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Therp BV <http://therp.nl>.
#
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Bank statement link partner',
    'version': '0.5',
    'license': 'AGPL-3',
    'author': 'Banking addons community',
    'website': 'https://github.com/OCA/bank-statement-reconcile',
    'category': 'Banking addons',
    'depends': [
        'account',
        ],
    'data': [
        'view/account_bank_statement.xml',
        'wizard/link_partner.xml',
    ],
    'js': [
    ],
    'installable': True,
    'auto_install': False,
}
