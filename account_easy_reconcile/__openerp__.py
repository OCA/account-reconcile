# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2012 Camptocamp SA (Guewen Baconnier)
#    Copyright (C) 2010   Sébastien Beau
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
    "name": "Easy Reconcile",
    "version": "1.3.1",
    "depends": ["account"],
    "author": "Akretion,Camptocamp",
    "description": """
Easy Reconcile
==============

This is a shared work between Akretion and Camptocamp
in order to provide:
 - reconciliation facilities for big volume of transactions
 - setup different profiles of reconciliation by account
 - each profile can use many methods of reconciliation
 - this module is also a base to create others
   reconciliation methods which can plug in the profiles
 - a profile a reconciliation can be run manually
   or by a cron
 - monitoring of reconciliation runs with an history
   which keep track of the reconciled Journal items

2 simple reconciliation methods are integrated
in this module, the simple reconciliations works
on 2 lines (1 debit / 1 credit) and do not allow
partial reconcilation, they also match on 1 key,
partner or Journal item name.

You may be interested to install also the
``account_advanced_reconciliation`` module.
This latter add more complex reconciliations,
allows multiple lines and partial.

""",
    "website": "http://www.akretion.com/",
    "category": "Finance",
    "demo_xml": [],
    "data": ["easy_reconcile.xml",
             "easy_reconcile_history_view.xml",
             "security/ir_rule.xml",
             "security/ir.model.access.csv",
             "res_config_view.xml",
             ],
    'license': 'AGPL-3',
    "auto_install": False,
    "installable": True,

}
