# -*- coding: utf-8 -*- ##############################################################################
#
#    Author: Nicolas Bessi, Joel Grand-Guillaume
#    Copyright 2011-2012 Camptocamp SA
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

{'name': "Advanced Reconcile",
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Finance',
 'complexity': 'normal',
 'depends': ['base_transaction_id', 'account_easy_reconcile'],
 'description': """
This module allows you auto reconcile entries with payment.
It is mostly used in E-Commerce, but could also be useful in other cases.

The automatic reconciliation matches a transaction ID, if available, propagated from the Sale Order.
It can also search for the sale order name in the origin or description of the move line.

Basically, this module will match account move line with a matching reference on a same account.
It will make a partial reconciliation if more than one move has the same reference (like 3x payments)
Once all payment will be there, it will make a full reconciliation.
You can choose a write-off amount as well.
 """,
 'website': 'http://www.camptocamp.com',
 'init_xml': [],
 'update_xml': [],
 'demo_xml': [],
 'test': [],
 'images': [],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
}
