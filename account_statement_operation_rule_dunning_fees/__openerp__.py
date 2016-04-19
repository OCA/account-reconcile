# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

{'name': 'Bank Statement Operation Rules with Dunning Fees',
 'version': '8.0.1.0.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Accounting & Finance',
 'depends': ['account_statement_operation_rule',
             # in https://github.com/OCA/account-financial-tools
             'account_credit_control_dunning_fees',
             ],
 'website': 'http://www.camptocamp.com',
 'data': ['view/account_statement_operation_rule_view.xml',
          ],
 'installable': True,
 'auto_install': True,
 }
