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
from datetime import datetime
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _


class easy_reconcile_options(orm.AbstractModel):
    """Options of a reconciliation profile

    Columns shared by the configuration of methods
    and by the reconciliation wizards.
    This allows decoupling of the methods and the
    wizards and allows to launch the wizards alone
    """

    _name = 'easy.reconcile.options'

    def _get_rec_base_date(self, cr, uid, context=None):
        return [('end_period_last_credit', 'End of period of most recent credit'),
                ('newest', 'Most recent move line'),
                ('actual', 'Today'),
                ('end_period', 'End of period of most recent move line'),
                ('newest_credit', 'Date of most recent credit'),
                ('newest_debit', 'Date of most recent debit')]

    _columns = {
            'write_off': fields.float('Write off allowed'),
            'account_lost_id': fields.many2one(
                'account.account', 'Account Lost'),
            'account_profit_id': fields.many2one(
                'account.account', 'Account Profit'),
            'journal_id': fields.many2one(
                'account.journal', 'Journal'),
            'date_base_on': fields.selection(
                _get_rec_base_date,
                required=True,
                string='Date of reconciliation'),
            'filter': fields.char('Filter', size=128),
            'analytic_account_id': fields.many2one(
                'account.analytic.account', 'Analytic Account',
                help="Analytic account for the write-off"),
    }

    _defaults = {
        'write_off': 0.,
        'date_base_on': 'end_period_last_credit',
    }


class account_easy_reconcile_method(orm.Model):

    _name = 'account.easy.reconcile.method'
    _description = 'reconcile method for account_easy_reconcile'

    _inherit = 'easy.reconcile.options'

    _order = 'sequence'

    def _get_all_rec_method(self, cr, uid, context=None):
        return [
            ('easy.reconcile.simple.name', 'Simple. Amount and Name'),
            ('easy.reconcile.simple.partner', 'Simple. Amount and Partner'),
            ('easy.reconcile.simple.reference', 'Simple. Amount and Reference'),
            ]

    def _get_rec_method(self, cr, uid, context=None):
        return self._get_all_rec_method(cr, uid, context=None)

    _columns = {
            'name': fields.selection(
                _get_rec_method, 'Type', required=True),
            'sequence': fields.integer(
                'Sequence',
                required=True,
                help="The sequence field is used to order "
                     "the reconcile method"),
            'task_id': fields.many2one(
                'account.easy.reconcile',
                string='Task',
                required=True,
                ondelete='cascade'),
            'company_id': fields.related('task_id','company_id',
                                         relation='res.company',
                                         type='many2one',
                                         string='Company',
                                         store=True,
                                         readonly=True),
    }

    _defaults = {
        'sequence': 1,
    }

    def init(self, cr):
        """ Migration stuff

        Name is not anymore methods names but the name
        of the model which does the reconciliation
        """
        cr.execute("""
        UPDATE account_easy_reconcile_method
        SET name = 'easy.reconcile.simple.partner'
        WHERE name = 'action_rec_auto_partner'
        """)
        cr.execute("""
        UPDATE account_easy_reconcile_method
        SET name = 'easy.reconcile.simple.name'
        WHERE name = 'action_rec_auto_name'
        """)


class account_easy_reconcile(orm.Model):

    _name = 'account.easy.reconcile'
    _description = 'account easy reconcile'

    def _get_total_unrec(self, cr, uid, ids, name, arg, context=None):
        obj_move_line = self.pool.get('account.move.line')
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = len(obj_move_line.search(
                cr, uid,
                [('account_id', '=', task.account.id),
                 ('reconcile_id', '=', False),
                 ('reconcile_partial_id', '=', False)],
                context=context))
        return res

    def _get_partial_rec(self, cr, uid, ids, name, arg, context=None):
        obj_move_line = self.pool.get('account.move.line')
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = len(obj_move_line.search(
                cr, uid,
                [('account_id', '=', task.account.id),
                 ('reconcile_id', '=', False),
                 ('reconcile_partial_id', '!=', False)],
                context=context))
        return res

    def _last_history(self, cr, uid, ids, name, args, context=None):
        result = {}
        for history in self.browse(cr, uid, ids, context=context):
            result[history.id] = False
            if history.history_ids:
                # history is sorted by date desc
                result[history.id] = history.history_ids[0].id
        return result

    _columns = {
        'name': fields.char('Name', required=True),
        'account': fields.many2one(
            'account.account', 'Account', required=True),
        'reconcile_method': fields.one2many(
            'account.easy.reconcile.method', 'task_id', 'Method'),
        'unreconciled_count': fields.function(
            _get_total_unrec, type='integer', string='Unreconciled Items'),
        'reconciled_partial_count': fields.function(
            _get_partial_rec,
            type='integer',
            string='Partially Reconciled Items'),
        'history_ids': fields.one2many(
            'easy.reconcile.history',
            'easy_reconcile_id',
            string='History',
            readonly=True),
        'last_history':
            fields.function(
                _last_history,
                string='Last History',
                type='many2one',
                relation='easy.reconcile.history',
                readonly=True),
        'company_id': fields.many2one('res.company', 'Company'),
    }

    def _prepare_run_transient(self, cr, uid, rec_method, context=None):
        return {'account_id': rec_method.task_id.account.id,
                'write_off': rec_method.write_off,
                'account_lost_id': (rec_method.account_lost_id and
                                    rec_method.account_lost_id.id),
                'account_profit_id': (rec_method.account_profit_id and
                                      rec_method.account_profit_id.id),
                'analytic_account_id': (rec_method.analytic_account_id and
                                        rec_method.analytic_account_id.id),
                'journal_id': (rec_method.journal_id and
                               rec_method.journal_id.id),
                'date_base_on': rec_method.date_base_on,
                'filter': rec_method.filter}

    def run_reconcile(self, cr, uid, ids, context=None):
        def find_reconcile_ids(fieldname, move_line_ids):
            if not move_line_ids:
                return []
            sql = ("SELECT DISTINCT " + fieldname +
                   " FROM account_move_line "
                   " WHERE id in %s "
                   " AND " + fieldname + " IS NOT NULL")
            cr.execute(sql, (tuple(move_line_ids),))
            res = cr.fetchall()
            return [row[0] for row in res]

        for rec in self.browse(cr, uid, ids, context=context):
            all_ml_rec_ids = []
            all_ml_partial_ids = []

            for method in rec.reconcile_method:
                rec_model = self.pool.get(method.name)
                auto_rec_id = rec_model.create(
                    cr, uid,
                    self._prepare_run_transient(
                        cr, uid, method, context=context),
                    context=context)

                ml_rec_ids, ml_partial_ids = rec_model.automatic_reconcile(
                    cr, uid, auto_rec_id, context=context)

                all_ml_rec_ids += ml_rec_ids
                all_ml_partial_ids += ml_partial_ids

            reconcile_ids = find_reconcile_ids(
                    'reconcile_id', all_ml_rec_ids)
            partial_ids = find_reconcile_ids(
                    'reconcile_partial_id', all_ml_partial_ids)

            self.pool.get('easy.reconcile.history').create(
                cr,
                uid,
                {'easy_reconcile_id': rec.id,
                 'date': fields.datetime.now(),
                 'reconcile_ids': [(4, rid) for rid in reconcile_ids],
                 'reconcile_partial_ids': [(4, rid) for rid in partial_ids]},
                context=context)
        return True

    def _no_history(self, cr, uid, rec, context=None):
        """ Raise an `osv.except_osv` error, supposed to
        be called when there is no history on the reconciliation
        task.
        """
        raise osv.except_osv(
                _('Error'),
                _('There is no history of reconciled '
                  'items on the task: %s.') % rec.name)

    def _open_move_line_list(sefl, cr, uid, move_line_ids, name, context=None):
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

    def open_unreconcile(self, cr, uid, ids, context=None):
        """ Open the view of move line with the unreconciled move lines
        """

        assert len(ids) == 1 , \
                "You can only open entries from one profile at a time"

        obj_move_line = self.pool.get('account.move.line')
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
             line_ids = obj_move_line.search(
                cr, uid,
                [('account_id', '=', task.account.id),
                 ('reconcile_id', '=', False),
                 ('reconcile_partial_id', '=', False)],
                context=context)

        name = _('Unreconciled items')
        return self._open_move_line_list(cr, uid, line_ids, name, context=context)

    def open_partial_reconcile(self, cr, uid, ids, context=None):
        """ Open the view of move line with the unreconciled move lines
        """

        assert len(ids) == 1 , \
                "You can only open entries from one profile at a time"

        obj_move_line = self.pool.get('account.move.line')
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
             line_ids = obj_move_line.search(
                cr, uid,
                [('account_id', '=', task.account.id),
                 ('reconcile_id', '=', False),
                 ('reconcile_partial_id', '!=', False)],
                context=context)
        name = _('Partial reconciled items')
        return self._open_move_line_list(cr, uid, line_ids, name, context=context)

    def last_history_reconcile(self, cr, uid, rec_id, context=None):
        """ Get the last history record for this reconciliation profile
        and return the action which opens move lines reconciled
        """
        if isinstance(rec_id, (tuple, list)):
            assert len(rec_id) == 1, \
                    "Only 1 id expected"
            rec_id = rec_id[0]
        rec = self.browse(cr, uid, rec_id, context=context)
        if not rec.last_history:
            self._no_history(cr, uid, rec, context=context)
        return rec.last_history.open_reconcile()

    def last_history_partial(self, cr, uid, rec_id, context=None):
        """ Get the last history record for this reconciliation profile
        and return the action which opens move lines reconciled
        """
        if isinstance(rec_id, (tuple, list)):
            assert len(rec_id) == 1, \
                    "Only 1 id expected"
            rec_id = rec_id[0]
        rec = self.browse(cr, uid, rec_id, context=context)
        if not rec.last_history:
            self._no_history(cr, uid, rec, context=context)
        return rec.last_history.open_partial()

    def run_scheduler(self, cr, uid, run_all=None, context=None):
        """ Launch the reconcile with the oldest run
        This function is mostly here to be used with cron task

        :param run_all: if set it will ingore lookup and launch
                    all reconciliation
        :returns: True in case of success or raises an exception

        """
        def _get_date(reconcile):
            return datetime.strptime(reconcile.last_history.date,
                                     DEFAULT_SERVER_DATETIME_FORMAT)

        ids = self.search(cr, uid, [], context=context)
        assert ids, "No easy reconcile available"
        if run_all:
            self.run_reconcile(cr, uid, ids, context=context)
            return True
        reconciles = self.browse(cr, uid, ids, context=context)
        reconciles.sort(key=_get_date)
        older = reconciles[0]
        self.run_reconcile(cr, uid, [older.id], context=context)
        return True
