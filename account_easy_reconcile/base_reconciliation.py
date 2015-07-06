# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2012-2013, 2015 Camptocamp SA (Guewen Baconnier, Damien Crier)
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

from openerp import models, api, fields
from openerp.tools.safe_eval import safe_eval
from operator import itemgetter, attrgetter


class EasyReconcileBase(models.AbstractModel):

    """Abstract Model for reconciliation methods"""

    _name = 'easy.reconcile.base'

    _inherit = 'easy.reconcile.options'

    account_id = fields.Many2one(
        'account.account',
        string='Account',
        required=True
    )
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Restrict on partners',
    )
    # other fields are inherited from easy.reconcile.options

    @api.multi
    def automatic_reconcile(self):
        """ Reconciliation method called from the view.

        :return: list of reconciled ids, list of partially reconciled items
        """
        self.ensure_one()
        return self._action_rec()

    @api.multi
    def _action_rec(self):
        """ Must be inherited to implement the reconciliation

        :return: list of reconciled ids
        """
        raise NotImplementedError

    def _base_columns(self):
        """ Mandatory columns for move lines queries
        An extra column aliased as ``key`` should be defined
        in each query."""
        aml_cols = (
            'id',
            'debit',
            'credit',
            'date',
            'period_id',
            'ref',
            'name',
            'partner_id',
            'account_id',
            'reconcile_partial_id',
            'move_id')
        return ["account_move_line.%s" % col for col in aml_cols]

    @api.multi
    def _select(self, *args, **kwargs):
        return "SELECT %s" % ', '.join(self._base_columns())

    @api.multi
    def _from(self, *args, **kwargs):
        return ("FROM account_move_line "
                "LEFT OUTER JOIN account_move_reconcile ON "
                "(account_move_line.reconcile_partial_id "
                "= account_move_reconcile.id)"
                )

    @api.multi
    def _where(self, *args, **kwargs):
        where = ("WHERE account_move_line.account_id = %s "
                 "AND COALESCE(account_move_reconcile.type,'') <> 'manual' "
                 "AND account_move_line.reconcile_id IS NULL ")
        # it would be great to use dict for params
        # but as we use _where_calc in _get_filter
        # which returns a list, we have to
        # accomodate with that
        params = [self.account_id.id]
        if self.partner_ids:
            where += " AND account_move_line.partner_id IN %s"
            params.append(tuple([l.id for l in self.partner_ids]))
        return where, params

    @api.multi
    def _get_filter(self):
        ml_obj = self.env['account.move.line']
        where = ''
        params = []
        if self.filter:
            dummy, where, params = ml_obj._where_calc(
                safe_eval(self.filter)).get_sql()
            if where:
                where = " AND %s" % where
        return where, params

    @api.multi
    def _below_writeoff_limit(self, lines, writeoff_limit):
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Account')
        keys = ('debit', 'credit')
        sums = reduce(
            lambda line, memo:
                dict((key, value + memo[key])
                     for key, value
                     in line.iteritems()
                     if key in keys), lines)
        debit, credit = sums['debit'], sums['credit']
        writeoff_amount = round(debit - credit, precision)
        return bool(writeoff_limit >= abs(writeoff_amount)), debit, credit

    @api.multi
    def _get_rec_date(self, lines, based_on='end_period_last_credit'):
        self.ensure_one()

        def last_period(mlines):
            period_ids = [ml['period_id'] for ml in mlines]
            periods = self.env['account.period'].browse(period_ids)
            return max(periods, key=attrgetter('date_stop'))

        def last_date(mlines):
            return max(mlines, key=itemgetter('date'))

        def credit(mlines):
            return [l for l in mlines if l['credit'] > 0]

        def debit(mlines):
            return [l for l in mlines if l['debit'] > 0]

        if based_on == 'end_period_last_credit':
            return last_period(credit(lines)).date_stop
        if based_on == 'end_period':
            return last_period(lines).date_stop
        elif based_on == 'newest':
            return last_date(lines)['date']
        elif based_on == 'newest_credit':
            return last_date(credit(lines))['date']
        elif based_on == 'newest_debit':
            return last_date(debit(lines))['date']
        # reconcilation date will be today
        # when date is None
        return None

    @api.multi
    def _reconcile_lines(self, lines, allow_partial=False):
        """ Try to reconcile given lines

        :param list lines: list of dict of move lines, they must at least
                           contain values for : id, debit, credit
        :param boolean allow_partial: if True, partial reconciliation will be
                                      created, otherwise only Full
                                      reconciliation will be created
        :return: tuple of boolean values, first item is wether the items
                 have been reconciled or not,
                 the second is wether the reconciliation is full (True)
                 or partial (False)
        """
        self.ensure_one()
        ml_obj = self.env['account.move.line']
        line_ids = [l['id'] for l in lines]
        below_writeoff, sum_debit, sum_credit = self._below_writeoff_limit(
            lines, self.write_off
        )
        date = self._get_rec_date(lines, self.date_base_on)
        rec_ctx = dict(self.env.context, date_p=date)
        if below_writeoff:
            if sum_credit > sum_debit:
                writeoff_account_id = self.account_profit_id.id
            else:
                writeoff_account_id = self.account_lost_id.id
            period_id = self.env['account.period'].find(dt=date)[0]
            if self.analytic_account_id:
                rec_ctx['analytic_id'] = self.analytic_account_id.id
            line_rs = ml_obj.browse(line_ids)
            line_rs.with_context(rec_ctx).reconcile(
                type='auto',
                writeoff_acc_id=writeoff_account_id,
                writeoff_period_id=period_id.id,
                writeoff_journal_id=self.journal_id.id
                )
            return True, True
        elif allow_partial:
            # Check if the group of move lines was already partially
            # reconciled and if all the lines were the same, in such
            # case, just skip the group and consider it as partially
            # reconciled (no change).
            if lines:
                existing_partial_id = lines[0]['reconcile_partial_id']
                if existing_partial_id:
                    partial_line_ids = set(ml_obj.search(
                        [('reconcile_partial_id', '=', existing_partial_id)],
                        ))
                    if set(line_ids) == partial_line_ids:
                        return True, False

            # We need to give a writeoff_acc_id
            # in case we have a multi currency lines
            # to reconcile.
            # If amount in currency is equal between
            # lines to reconcile
            # it will do a full reconcile instead of a partial reconcile
            # and make a write-off for exchange
            if sum_credit > sum_debit:
                writeoff_account_id = self.income_exchange_account_id.id
            else:
                writeoff_account_id = self.expense_exchange_account_id.id
            period_id = self.env['account.period'].find(dt=date)[0]
            if self.analytic_account_id:
                rec_ctx['analytic_id'] = self.analytic_account_id.id
            line_rs = ml_obj.browse(line_ids)
            line_rs.with_context(rec_ctx).reconcile(
                type='manual',
                writeoff_acc_id=writeoff_account_id,
                writeoff_period_id=period_id.id,
                writeoff_journal_id=self.journal_id.id
                )
            return True, False
        return False, False
