# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier, Damien Crier
#    Copyright 2012, 2015 Camptocamp SA
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

from openerp import models, api, fields, _


class EasyReconcileHistory(models.Model):
    """ Store an history of the runs per profile
    Each history stores the list of reconciliations done"""

    _name = 'easy.reconcile.history'
    _rec_name = 'easy_reconcile_id'
    _order = 'date DESC'

    @api.one
    @api.depends('reconcile_ids', 'reconcile_partial_ids')
    def _get_reconcile_line_ids(self):
        move_line_ids = []
        for reconcile in self.reconcile_ids:
            move_lines = reconcile.mapped('line_id')
            move_line_ids.extend(move_lines.ids)
        self.reconcile_line_ids = move_line_ids

        move_line_ids2 = []
        for reconcile2 in self.reconcile_partial_ids:
            move_lines2 = reconcile2.mapped('line_partial_ids')
            move_line_ids2.extend(move_lines2.ids)
        self.partial_line_ids = move_line_ids2

    easy_reconcile_id = fields.Many2one(
        'account.easy.reconcile',
        string='Reconcile Profile',
        readonly=True
    )
    date = fields.Datetime(string='Run date', readonly=True, required=True)
    reconcile_ids = fields.Many2many(
        comodel_name='account.move.reconcile',
        relation='account_move_reconcile_history_rel',
        string='Partial Reconciliations',
        readonly=True
    )
    reconcile_partial_ids = fields.Many2many(
        comodel_name='account.move.reconcile',
        relation='account_move_reconcile_history_partial_rel',
        string='Partial Reconciliations',
        readonly=True
    )
    reconcile_line_ids = fields.Many2many(
        comodel_name='account.move.line',
        relation='account_move_line_history_rel',
        string='Reconciled Items',
        compute='_get_reconcile_line_ids'
    )
    partial_line_ids = fields.Many2many(
        comodel_name='account.move.line',
        relation='account_move_line_history_partial_rel',
        string='Partially Reconciled Items',
        compute='_get_reconcile_line_ids'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        store=True,
        readonly=True,
        related='easy_reconcile_id.company_id'
    )

    @api.multi
    def _open_move_lines(self, rec_type='full'):
        """ For an history record, open the view of move line with
        the reconciled or partially reconciled move lines

        :param history_id: id of the history
        :param rec_type: 'full' or 'partial'
        :return: action to open the move lines
        """
        assert rec_type in ('full', 'partial'), \
            "rec_type must be 'full' or 'partial'"
        move_line_ids = []
        if rec_type == 'full':
            move_line_ids = self.mapped('reconcile_ids.line_id').ids
            name = _('Reconciliations')
        else:
            move_line_ids = self.mapped(
                'reconcile_partial_ids.line_partial_ids').ids
            name = _('Partial Reconciliations')
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

    @api.multi
    def open_reconcile(self):
        """ For an history record, open the view of move line
        with the reconciled move lines

        :param history_ids: id of the record as int or long
                            Accept a list with 1 id too to be
                            used from the client.
        """
        self.ensure_one()
        return self._open_move_lines(rec_type='full')

    @api.multi
    def open_partial(self):
        """ For an history record, open the view of move line
        with the partially reconciled move lines

        :param history_ids: id of the record as int or long
                            Accept a list with 1 id too to be
                            used from the client.
        """
        self.ensure_one()
        return self._open_move_lines(rec_type='partial')
