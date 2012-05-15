# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher (Camptocamp)
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

{'name': 'Base transaction id for financial institutes',
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Hidden/Dependency',
 'complexity': 'easy', #easy, normal, expert
 'depends': ['account', 'sale'],
 'description': """Adds transaction id to invoice and sale models and views""",
 'website': 'http://www.openerp.com',
 'init_xml': [],
 'update_xml': ['invoice_view.xml', 'sale_view.xml'],
 'demo_xml': [],
 'test': [],
 'installable': True,
 'images': [],
 'auto_install': False,
 'license': 'AGPL-3',
 'active': False,
}
