# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of account_statement_partner_lines,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_statement_partner_lines is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     account_statement_partner_lines is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with account_statement_partner_lines.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Account Statement Partner Lines",
    'summary': """
        View partner's move line from bank statement reconcile widget""",
    'author': "ACSONE SA/NV,Odoo Community Association (OCA)",
    'website': "http://acsone.eu",
    'category': 'Accounting',
    'version': '0.1',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_statement_partner_lines.xml',
    ],
    'qweb': [
        'static/src/xml/templates.xml',
    ],
}
