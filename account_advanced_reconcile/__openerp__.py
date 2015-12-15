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
 'summary': "Reconcile: with multiple lines / partial / with writeoffs",
 'version': '1.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Finance',
 'complexity': 'normal',
 'depends': ['account_easy_reconcile',
             ],
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
