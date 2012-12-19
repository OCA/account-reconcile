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

from openerp.osv import orm, fields


class easy_reconcile_history(orm.Model):
    """ Store an history of the runs per profile
    Each history stores the list of reconciliations done"""

    _name = 'easy.reconcile.history'

    _columns = {
            'easy_reconcile_id': fields.many2one(
                'account.easy.reconcile', 'Reconcile Profile', readonly=True),
            'date': fields.datetime('Run date', readonly=True),
            'reconcile_ids': fields.many2many(
                'account.move.reconcile', string='Reconciliations', readonly=True),
            'reconcile_partial_ids': fields.many2many(
                'account.move.reconcile', string='Partial Reconciliations', readonly=True),
        }
