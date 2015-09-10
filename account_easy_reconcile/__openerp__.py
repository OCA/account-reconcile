# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2012, 2015 Camptocamp SA (Guewen Baconnier, Damien Crier)
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
    "version": "8.0.1.3.1",
    "depends": ["account"],
    "author": "Akretion,Camptocamp,Odoo Community Association (OCA)",
    "website": "http://www.akretion.com/",
    "category": "Finance",
    "data": ["easy_reconcile.xml",
             "easy_reconcile_history_view.xml",
             "security/ir_rule.xml",
             "security/ir.model.access.csv",
             "res_config_view.xml",
             ],
    "test": ['test/easy_reconcile.yml',
             ],
    'license': 'AGPL-3',
    "auto_install": False,
    'installable': True,

}
