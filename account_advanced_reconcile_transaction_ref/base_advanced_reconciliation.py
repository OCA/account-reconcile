# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Romain Deheele
#    Copyright 2013 Camptocamp SA
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


class EasyReconcileAdvanced(orm.AbstractModel):

    _inherit = 'easy.reconcile.advanced'

    def _base_columns(self, rec):
        """ Mandatory columns for move lines queries
        An extra column aliased as ``key`` should be defined
        in each query."""
        aml_cols = super(EasyReconcileAdvanced, self)._base_columns(rec)
        aml_cols.append('account_move_line.transaction_ref')
        return aml_cols
