# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume
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

{'name': "Bank statement extension with voucher",
 'version': '1.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Finance',
 'complexity': 'normal',
 'depends': [
     'account_statement_base_completion',
     'account_voucher'
 ],
 'description': """
 This module is only needed when using account_statement_base_completion with
 voucher in order adapt the view correctly.
 """,
 'website': 'http://www.camptocamp.com',
 'init_xml': [],
 'update_xml': [
     "statement_view.xml",
 ],
 'demo_xml': [],
 'test': [],
 'installable': False,
 'images': [],
 'auto_install': False,
 'license': 'AGPL-3',
 }
