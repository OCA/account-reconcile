# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Contributor: Leonardo Pistone
#    Copyright 2012-2014 Camptocamp SA
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
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Finance',
 'complexity': 'normal',
 'depends': ['account_easy_reconcile',
             ],
 'description': """
Advanced reconciliation methods for the module account_easy_reconcile.

In addition to the features implemented in account_easy_reconcile, which are:
 - reconciliation facilities for big volume of transactions
 - setup different profiles of reconciliation by account
 - each profile can use many methods of reconciliation
 - this module is also a base to create others reconciliation methods
    which can plug in the profiles
 - a profile a reconciliation can be run manually or by a cron
 - monitoring of reconcilation runs with an history

It implements a basis to created advanced reconciliation methods in a few lines
of code.

Typically, such a method can be:
 - Reconcile Journal items if the partner and the ref are equal
 - Reconcile Journal items if the partner is equal and the ref
   is the same than ref or name
 - Reconcile Journal items if the partner is equal and the ref
   match with a pattern

And they allows:
 - Reconciliations with multiple credit / multiple debit lines
 - Partial reconciliations
 - Write-off amount as well

A method is already implemented in this module, it matches on items:
 - Partner
 - Ref on credit move lines should be case insensitive equals to the ref or
   the name of the debit move line

The base class to find the reconciliations is built to be as efficient as
possible.

So basically, if you have an invoice with 3 payments (one per month), the first
month, it will partial reconcile the debit move line with the first payment,
the second month, it will partial reconcile the debit move line with 2 first
payments, the third month, it will make the full reconciliation.

This module is perfectly adapted for E-Commerce business where a big volume of
move lines and so, reconciliations, are involved and payments often come from
many offices.

 """,
 'website': 'http://www.camptocamp.com',
 'data': ['easy_reconcile_view.xml',
          ],
 'test': [],
 'images': [],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': True,
 }
