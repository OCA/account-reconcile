# -*- coding: utf-8 -*-
###############################################################################
#
#   account_statement_completion_label for OpenERP
#   Copyright (C) 2013 Akretion (http://www.akretion.com). All Rights Reserved
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
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
    'name': 'Bank statement completion from label',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """
    Improve the basic rule "Match from statement line label (based on partner
    field 'Bank Statement Label')" provided by the Bank statement base
    completion module. The goal is to match the label field from the bank
    statement line with a partner and an account.
    For this, you have to create your record in the new class
    account.statement.label where you can link the label you want with a
    partner and an account.

    """,
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['account_statement_base_completion'],
    'data': [
        'partner_view.xml',
        'statement_view.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
    ],
    'demo': [],
    'installable': False,
    'active': False,
}
