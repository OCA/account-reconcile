# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2012 Camptocamp SA
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
 'depends': ['account_easy_reconcile'],
 'description': """
Advanced reconciliation methods for the module account_easy_reconcile.

It implements a basis to created advanced reconciliation methods in a few lines
of code.

Typically, such a method can be:
 - Reconcile entries if the partner and the ref are equal
 - Reconcile entries if the partner is equal and the ref is the same than ref
   or name
 - Reconcile entries if the partner is equal and the ref match with a pattern

A method is already implemented in this module, it matches on entries:
 * Partner
 * Ref on credit move lines should be case insensitive equals to the ref or
   the name of the debit move line

The base class to find the reconciliations is built to be as efficient as
possible.

Reconciliations with multiple credit / debit lines is possible.
Partial reconciliation are generated.
You can choose a write-off amount as well.

So basically, if you have an invoice with 3 payments (one per month), the first
month, it will partial reconcile the debit move line with the first payment, the second
month, it will partial reconcile the debit move line with 2 first payments,
the third month, it will make the full reconciliation.

This module is perfectly adapted for E-Commerce business where a big volume of
move lines and so, reconciliations, is involved and payments often come from
many offices.
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
 'application': True,
}
