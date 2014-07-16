# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
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

{'name': 'Advanced Reconcile Bank Statement',
 'description':  """
Advanced reconciliation method for the module account_advanced_reconcile
========================================================================
Reconcile rules with bank statement name.

This will reconcile multiple credit move lines (bank statements) with
all the lines from a specific bank statement, debit or credit (to also
reconcile the commission with credit card imports).

""",
 'version': '1.0.0',
 'author': 'Camptocamp',
 'category': 'Finance',
 'website': 'http://www.camptocamp.com',
 'depends': ['account_advanced_reconcile'],
 'data': ['easy_reconcile_view.xml'],
 'demo': [],
 'test': [], # To be ported or migrate to unit tests or scenarios
 'auto_install': False,
 'installable': True,
 'images': []
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
