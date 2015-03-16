# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Therp BV (<http://therp.nl>) / BAS Solutions
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': 'Default partner journal accounts for bank transactions',
    'version': '1.0',
    'license': 'AGPL-3',
    'author': "Therp BV,BAS Solutions,Odoo Community Association (OCA)",
    'category': 'Banking',
    'depends': ['base', 'account'],
    'description': '''
This module allows to set alternative journal accounts on partners to use
as default on bank statements.

This is useful when regular transactions on clearing accounts occur. Such
clearing accounts cannot usually be selected as default partner accounts
because they are neither of type 'payable' nor 'receivable' (or at least
never at the same time!). For the alternative journal accounts for bank
transactions, any reconcilable account can be selected.
    ''',
    'data': [
        'res_partner_view.xml',
        'account.xml'
    ],
    'installable': True,
}
