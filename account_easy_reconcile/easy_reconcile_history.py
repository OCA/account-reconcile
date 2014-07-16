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
from openerp.tools.translate import _


class easy_reconcile_history(orm.Model):
    """ Store an history of the runs per profile
    Each history stores the list of reconciliations done"""

    _name = 'easy.reconcile.history'
    _rec_name = 'easy_reconcile_id'
    _order = 'date DESC'

    def _reconcile_line_ids(self, cr, uid, ids, name, args, context=None):
        result = {}

        for history in self.browse(cr, uid, ids, context=context):
            result[history.id] = {}

            move_line_ids = []
            for reconcile in history.reconcile_ids:
                move_line_ids += [line.id
                                    for line
                                    in reconcile.line_id]
            result[history.id]['reconcile_line_ids'] = move_line_ids

            move_line_ids = []
            for reconcile in history.reconcile_partial_ids:
                move_line_ids += [line.id
                                    for line
                                    in reconcile.line_partial_ids]
            result[history.id]['partial_line_ids'] = move_line_ids

        return result

    _columns = {
            'easy_reconcile_id': fields.many2one(
                'account.easy.reconcile', 'Reconcile Profile', readonly=True),
            'date': fields.datetime('Run date', readonly=True, required=True),
            'reconcile_ids': fields.many2many(
                'account.move.reconcile',
                'account_move_reconcile_history_rel',
                string='Reconciliations', readonly=True),
            'reconcile_partial_ids': fields.many2many(
                'account.move.reconcile',
                'account_move_reconcile_history_partial_rel',
                string='Partial Reconciliations', readonly=True),
            'reconcile_line_ids':
                fields.function(
                    _reconcile_line_ids,
                    string='Reconciled Items',
                    type='many2many',
                    relation='account.move.line',
                    readonly=True,
                    multi='lines'),
            'partial_line_ids':
                fields.function(
                    _reconcile_line_ids,
                    string='Partially Reconciled Items',
                    type='many2many',
                    relation='account.move.line',
                    readonly=True,
                    multi='lines'),
            'company_id': fields.related('easy_reconcile_id','company_id',
                                         relation='res.company',
                                         type='many2one',
                                         string='Company',
                                         store=True,
                                         readonly=True),

        }

    def _open_move_lines(self, cr, uid, history_id, rec_type='full', context=None):
        """ For an history record, open the view of move line with
        the reconciled or partially reconciled move lines

        :param history_id: id of the history
        :param rec_type: 'full' or 'partial'
        :return: action to open the move lines
        """
        assert rec_type in ('full', 'partial'), \
                "rec_type must be 'full' or 'partial'"

        history = self.browse(cr, uid, history_id, context=context)

        if rec_type == 'full':
            field = 'reconcile_line_ids'
            name = _('Reconciliations')
        else:
            field = 'partial_line_ids'
            name = _('Partial Reconciliations')

        move_line_ids = [line.id for line in getattr(history, field)]

        return {
            'name': name,
            'view_mode': 'tree,form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': unicode([('id', 'in', move_line_ids)]),
            }

    def open_reconcile(self, cr, uid, history_ids, context=None):
        """ For an history record, open the view of move line
        with the reconciled move lines

        :param history_ids: id of the record as int or long
                            Accept a list with 1 id too to be
                            used from the client.
        """
        if isinstance(history_ids, (tuple, list)):
            assert len(history_ids) == 1, "only 1 ID is accepted"
            history_ids = history_ids[0]
        return self._open_move_lines(
                cr, uid, history_ids, rec_type='full', context=None)

    def open_partial(self, cr, uid, history_ids, context=None):
        """ For an history record, open the view of move line
        with the partially reconciled move lines

        :param history_ids: id of the record as int or long
                            Accept a list with 1 id too to be
                            used from the client.
        """
        if isinstance(history_ids, (tuple, list)):
            assert len(history_ids) == 1, "only 1 ID is accepted"
            history_ids = history_ids[0]
        return self._open_move_lines(
                cr, uid, history_ids, rec_type='partial', context=None)
