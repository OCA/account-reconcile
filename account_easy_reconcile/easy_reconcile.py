# -*- encoding: utf-8 -*-
#########################################################################
#                                                                       #
# Copyright (C) 2010   Sébastien Beau                                   #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################

import time
import string
from osv import fields, osv
from tools.translate import _
from tools import DEFAULT_SERVER_DATETIME_FORMAT
from operator import itemgetter, attrgetter


class account_easy_reconcile_method(osv.osv):
    _name = 'account.easy.reconcile.method'
    _description = 'reconcile method for account_easy_reconcile'

    def onchange_name(self, cr, uid, id, name, write_off, context=None):
        if name in ['action_rec_auto_name', 'action_rec_auto_partner']:
            if write_off>0:
                return {'value': {'require_write_off': True, 'require_account_id': True, 'require_journal_id': True}}
            return {'value': {'require_write_off': True}}
        return {}

    def onchange_write_off(self, cr, uid, id, name, write_off, context=None):
        if name in ['action_rec_auto_name', 'action_rec_auto_partner']:
            if write_off>0:
                return {'value': {'require_account_id': True, 'require_journal_id': True}}
            else:
                return {'value': {'require_account_id': False, 'require_journal_id': False}}
        return {}

    def _get_all_rec_method(self, cr, uid, context=None):
        return [
            ('action_rec_auto_name', 'Simple method based on amount and name'),
            ('action_rec_auto_partner', 'Simple method based on amount and partner'),
            ]

    def _get_rec_method(self, cr, uid, context=None):
        return self._get_all_rec_method(cr, uid, context=None)

    _columns = {
            'name': fields.selection(_get_rec_method, 'Type', size=128, required=True),
            'sequence': fields.integer('Sequence', required=True, help="The sequence field is used to order the reconcile method"),
            'write_off': fields.float('Write off Value'),
            'account_lost_id': fields.many2one('account.account', 'Account Lost'),
            'account_profit_id': fields.many2one('account.account', 'Account Profit'),
            'journal_id': fields.many2one('account.journal', 'Journal'),
            'require_write_off': fields.boolean('Require Write-off'),
            'require_account_id': fields.boolean('Require Account'),
            'require_journal_id': fields.boolean('Require Journal'),
            'date_base_on': fields.selection(
                [('newest', 'Most recent move line'),
                 ('actual', 'Today'),
                 ('end_period_last_credit', 'End of period of most recent credit'),
                 ('end_period', 'End of period of most recent move line'),
                 ('newest_credit', 'Date of most recent credit'),
                 ('newest_debit', 'Date of most recent debit')],
                 string='Date of reconcilation'),
            'filter': fields.char('Filter', size=128),
    }

    _defaults = {
        'write_off': lambda *a: 0,
    }

    _order = 'sequence'

account_easy_reconcile_method()


class account_easy_reconcile(osv.osv):
    _name = 'account.easy.reconcile'
    _description = 'account easy reconcile'

    def _get_unrec_number(self, cr, uid, ids, name, arg, context=None):
        obj_move_line = self.pool.get('account.move.line')
        res={}
        for task in self.read(cr, uid, ids, ['account'], context=context):
            res[task['id']] = len(obj_move_line.search(cr, uid, [('account_id', '=', task['account'][0]), ('reconcile_id', '=', False)], context=context))
        return res

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'account': fields.many2one('account.account', 'Account', required=True),
        'reconcile_method': fields.one2many('account.easy.reconcile.method', 'task_id', 'Method'),
        'scheduler': fields.many2one('ir.cron', 'scheduler', readonly=True),
        'rec_log': fields.text('log', readonly=True),
        'unreconcile_entry_number': fields.function(_get_unrec_number, method=True, type='integer', string='Unreconcile Entries'),
    }

    def _below_writeoff_limit(self, cr, uid, lines,
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

    def _get_rec_date(self, cr, uid, lines, based_on='end_period_last_credit', context=None):
        period_obj = self.pool.get('account.period')

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

    def _reconcile_lines(self, cr, uid, lines, allow_partial=False, context=None):
        if context is None:
            context = {}

        ml_obj = self.pool.get('account.move.line')
        writeoff = context.get('write_off', 0.)

        keys = ('debit', 'credit')

        line_ids = [l['id'] for l in lines]
        below_writeoff, sum_debit, sum_credit = self._below_writeoff_limit(
            cr, uid, lines, writeoff, context=context)
        date = self._get_rec_date(
            cr, uid, lines, context.get('date_base_on'), context=context)

        rec_ctx = dict(context, date_p=date)
        if below_writeoff:
            if sum_credit < sum_debit:
                writeoff_account_id = context.get('account_profit_id', False)
            else:
                writeoff_account_id = context.get('account_lost_id', False)

            period_id = self.pool.get('account.period').find(
                cr, uid, dt=date, context=context)[0]

            ml_obj.reconcile(
                cr, uid,
                line_ids,
                type='auto',
                writeoff_acc_id=writeoff_account_id,
                writeoff_period_id=period_id,
                writeoff_journal_id=context.get('journal_id'),
                context=rec_ctx)
            return True
        elif allow_partial:
            ml_obj.reconcile_partial(
                cr, uid,
                line_ids,
                type='manual',
                context=rec_ctx)
            return True

        return False

    def rec_auto_lines_simple(self, cr, uid, lines, context=None):
        if context is None:
            context = {}

        count = 0
        res = 0
        while (count < len(lines)):
            for i in range(count+1, len(lines)):
                writeoff_account_id = False
                if lines[count]['key'] != lines[i]['key']:
                    break

                check = False
                if lines[count]['credit'] > 0 and lines[i]['debit'] > 0:
                    credit_line = lines[count]
                    debit_line = lines[i]
                    check = True
                elif lines[i]['credit'] > 0  and lines[count]['debit'] > 0:
                    credit_line = lines[i]
                    debit_line = lines[count]
                    check = True
                if not check:
                    continue

                if self._reconcile_lines(cr, uid, [credit_line, debit_line],
                        allow_partial=False, context=context):
                    res += 2
                    del lines[i]
                    break
            count += 1
        return res

    def _get_filter(self, cr, uid, account_id, context):
        ml_obj = self.pool.get('account.move.line')
        where = ''
        params = []
        if context.get('filter'):
            dummy, where, params = ml_obj._where_calc(
                cr, uid, context['filter'], context=context).get_sql()
            if where:
                where = " AND %s" % where
        return where, params

    def _base_columns(self, easy_rec):
        """Mandatory columns for move lines queries
        An extra column aliased as `key` should be defined
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
            'move_id')
        return ["account_move_line.%s" % col for col in aml_cols]

    def _base_select(self, easy_rec, *args, **kwargs):
        return "SELECT %s" % ', '.join(self._base_columns(easy_rec))

    def _base_from(self, easy_rec, *args, **kwargs):
        return "FROM account_move_line"

    def _base_where(self, easy_rec, *args, **kwargs):
        where = ("WHERE account_move_line.account_id = %s "
                 "AND account_move_line.reconcile_id IS NULL ")
        # it would be great to use dict for params
        # but as we use _where_calc in _get_filter
        # which returns a list, we have to
        # accomodate with that
        params = [easy_rec.account.id]
        return where, params

    def _simple_order(self, easy_rec, key, *args, **kwargs):
        return "ORDER BY account_move_line.%s" % key

    def _action_rec_simple(self, cr, uid, easy_rec, key, context=None):
        """Match only 2 move lines, do not allow partial reconcile"""
        select = self._base_select(easy_rec)
        select += ", account_move_line.%s as key " % key
        where, params = self._base_where(easy_rec)
        where += " AND account_move_line.%s IS NOT NULL " % key

        where2, params2 = self._get_filter(cr, uid, easy_rec, context=context)
        query = ' '.join((
            select,
            self._base_from(easy_rec),
            where, where2,
            self._simple_order(easy_rec, key)))

        cr.execute(query, params + params2)
        lines = cr.dictfetchall()
        return self.rec_auto_lines_simple(cr, uid, lines, context)

    def _action_rec_auto_name(self, cr, uid, easy_rec, context):
        return self._action_rec_simple(
            cr, uid, easy_rec, 'name', context=context)

    def _action_rec_auto_partner(self, cr, uid, easy_rec, context):
        return self._action_rec_simple(
            cr, uid, easy_rec, 'partner_id', context=context)

    def action_rec_auto(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for rec_id in ids:
            rec = self.browse(cr, uid, rec_id, context=context)
            total_rec = 0
            details = ''
            count = 0
            for method in rec.reconcile_method:
                count += 1
                ctx = dict(
                    context,
                    date_base_on=method.date_base_on,
                    filter=eval(method.filter or '[]'),
                    write_off=(method.write_off > 0 and method.write_off) or 0,
                    account_lost_id=method.account_lost_id.id,
                    account_profit_id=method.account_profit_id.id,
                    journal_id=method.journal_id.id)

                py_meth = getattr(self, "_%s" % method.name)
                res = py_meth(cr, uid, rec, context=ctx)
                details += _(' method %d : %d lines |') % (count, res)
            log = self.read(cr, uid, rec_id, ['rec_log'], context=context)['rec_log']
            log_lines = log and log.splitlines() or []
            log_lines[0:0] = [_('%s : %d lines have been reconciled (%s)') %
                (time.strftime(DEFAULT_SERVER_DATETIME_FORMAT), total_rec, details[0:-2])]
            log = "\n".join(log_lines)
            self.write(cr, uid, rec_id, {'rec_log': log}, context=context)
        return True

account_easy_reconcile()


class account_easy_reconcile_method(osv.osv):

    _inherit = 'account.easy.reconcile.method'

    _columns = {
            'task_id': fields.many2one('account.easy.reconcile', 'Task', required=True, ondelete='cascade'),
    }

account_easy_reconcile_method()

