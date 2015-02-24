# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2012-2013 Camptocamp SA (Guewen Baconnier)
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

from openerp.osv import fields, orm
from operator import itemgetter, attrgetter


class EasyReconcileBase(orm.AbstractModel):

    """Abstract Model for reconciliation methods"""

    _name = 'easy.reconcile.base'

    _inherit = 'easy.reconcile.options'

    _columns = {
        'account_id': fields.many2one(
            'account.account', 'Account', required=True),
        'partner_ids': fields.many2many(
            'res.partner', string="Restrict on partners"),
        # other columns are inherited from easy.reconcile.options
    }

    def automatic_reconcile(self, cr, uid, ids, context=None):
        """ Reconciliation method called from the view.

        :return: list of reconciled ids, list of partially reconciled items
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        assert len(ids) == 1, "Has to be called on one id"
        rec = self.browse(cr, uid, ids[0], context=context)
        return self._action_rec(cr, uid, rec, context=context)

    def _action_rec(self, cr, uid, rec, context=None):
        """ Must be inherited to implement the reconciliation

        :return: list of reconciled ids
        """
        raise NotImplementedError

    def _base_columns(self, rec):
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

    def _select(self, rec, *args, **kwargs):
        return "SELECT %s" % ', '.join(self._base_columns(rec))

    def _from(self, rec, *args, **kwargs):
        return ("FROM account_move_line "
                "LEFT OUTER JOIN account_move_reconcile ON "
                "(account_move_line.reconcile_partial_id "
                "= account_move_reconcile.id)"
                )

    def _where(self, rec, *args, **kwargs):
        where = ("WHERE account_move_line.account_id = %s "
                 "AND COALESCE(account_move_reconcile.type,'') <> 'manual' "
                 "AND account_move_line.reconcile_id IS NULL "
                 "AND account_move_line.state != 'draft' ")
        # it would be great to use dict for params
        # but as we use _where_calc in _get_filter
        # which returns a list, we have to
        # accomodate with that
        params = [rec.account_id.id]
        if rec.partner_ids:
            where += " AND account_move_line.partner_id IN %s"
            params.append(tuple([l.id for l in rec.partner_ids]))
        return where, params

    def _get_filter(self, cr, uid, rec, context):
        ml_obj = self.pool.get('account.move.line')
        where = ''
        params = []
        if rec.filter:
            dummy, where, params = ml_obj._where_calc(
                cr, uid, eval(rec.filter), context=context).get_sql()
            if where:
                where = " AND %s" % where
        return where, params

    def _below_writeoff_limit(self, cr, uid, rec, lines,
                              writeoff_limit, context=None):
        precision = self.pool.get('decimal.precision').precision_get(
            cr, uid, 'Account')
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

    def _check_period_state(self, cr, uid, date, context=None):
        period_id = self.pool['account.period'].find(
            cr, uid, dt=date, context=context)[0]
        cr.execute("""
            SELECT state
            FROM account_period
            WHERE id = %s
        """, (period_id,))

        state = cr.fetchall()[0][0]
        if state == 'done':
            return False
        else:
            return True

    def _get_open_period_date(self, cr, uid, date, context=None):
        cr.execute("""
            SELECT date_start
            FROM account_period
            WHERE state = 'draft'
                AND date_start > %s
            ORDER BY date_start asc
            LIMIT 1
        """, (date,))

        first_date_available = cr.fetchall()
        if first_date_available:
            return first_date_available[0][0]
        else:
            return date

    def _get_rec_date(self, cr, uid, rec, lines,
                      based_on='end_period_last_credit', context=None):
        period_obj = self.pool['account.period']
        date = None

        def last_period(mlines):
            period_ids = [ml['period_id'] for ml in mlines]
            periods = period_obj.browse(
                cr, uid, period_ids, context=context)
            return max(periods, key=attrgetter('date_stop'))

        def last_date(mlines):
            return max(mlines, key=itemgetter('date'))

        def credit(mlines):
            return [l for l in mlines if l['credit'] > 0]

        def debit(mlines):
            return [l for l in mlines if l['debit'] > 0]

        if based_on == 'end_period_last_credit':
            date = last_period(credit(lines)).date_stop
        if based_on == 'end_period':
            date = last_period(lines).date_stop
        elif based_on == 'newest':
            date = last_date(lines)['date']
        elif based_on == 'newest_credit':
            date = last_date(credit(lines))['date']
        elif based_on == 'newest_debit':
            date = last_date(debit(lines))['date']

        if date:
            if not self._check_period_state(cr, uid, date, context=context):
                date = self._get_open_period_date(
                    cr, uid, date, context=context)
        # reconcilation date will be today
        # when date is None
        return date

    def _reconcile_lines(self, cr, uid, rec, lines, allow_partial=False,
                         context=None):
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
        if context is None:
            context = {}
        ml_obj = self.pool.get('account.move.line')
        writeoff = rec.write_off
        line_ids = [l['id'] for l in lines]
        below_writeoff, sum_debit, sum_credit = self._below_writeoff_limit(
            cr, uid, rec, lines, writeoff, context=context)
        date = self._get_rec_date(
            cr, uid, rec, lines, rec.date_base_on, context=context)
        rec_ctx = dict(context, date_p=date)
        if below_writeoff:
            if sum_credit > sum_debit:
                writeoff_account_id = rec.account_profit_id.id
            else:
                writeoff_account_id = rec.account_lost_id.id
            period_id = self.pool.get('account.period').find(
                cr, uid, dt=date, context=context)[0]
            if rec.analytic_account_id:
                rec_ctx['analytic_id'] = rec.analytic_account_id.id
            ml_obj.reconcile(
                cr, uid,
                line_ids,
                type='auto',
                writeoff_acc_id=writeoff_account_id,
                writeoff_period_id=period_id,
                writeoff_journal_id=rec.journal_id.id,
                context=rec_ctx)
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
                        cr, uid,
                        [('reconcile_partial_id', '=', existing_partial_id)],
                        context=context))
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
                writeoff_account_id = rec.income_exchange_account_id.id
            else:
                writeoff_account_id = rec.expense_exchange_account_id.id
            period_id = self.pool['account.period'].find(
                cr, uid, dt=date, context=context)[0]
            if rec.analytic_account_id:
                rec_ctx['analytic_id'] = rec.analytic_account_id.id
            ml_obj.reconcile_partial(
                cr, uid,
                line_ids,
                type='manual',
                writeoff_acc_id=writeoff_account_id,
                writeoff_period_id=period_id,
                writeoff_journal_id=rec.journal_id.id,
                context=rec_ctx)
            return True, False
        return False, False
