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

from openerp.osv.orm import Model


class account_easy_reconcile_method(Model):

    _inherit = 'account.easy.reconcile.method'

    def _get_all_rec_method(self, cr, uid, context=None):
        methods = super(account_easy_reconcile_method, self).\
            _get_all_rec_method(cr, uid, context=context)
        methods += [
            ('easy.reconcile.advanced.ref',
            'Advanced method, payment ref matches with ref or name'),
            ('easy.reconcile.advanced.tid',
            'Advanced method, payment Transaction ID matches with ref or name')
        ]
        return methods
