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

from openerp.osv import orm


class account_easy_reconcile_method(orm.Model):

    _inherit = 'account.easy.reconcile.method'

    def _get_all_rec_method(self, cr, uid, context=None):
        methods = super(account_easy_reconcile_method, self).\
            _get_all_rec_method(cr, uid, context=context)
        methods += [
            ('easy.reconcile.advanced.bank_statement',
             'Advanced. Partner and Bank Statement'),
        ]
        return methods

