# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2012 Camptocamp SA (Guewen Baconnier)
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

import time
from openerp.osv.orm import Model
from openerp.osv import fields
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class account_easy_reconcile_method(Model):

    _name = 'account.easy.reconcile.method'
    _description = 'reconcile method for account_easy_reconcile'

    def _get_all_rec_method(self, cr, uid, context=None):
        return [
            ('easy.reconcile.simple.name', 'Simple method based on amount and name'),
            ('easy.reconcile.simple.partner', 'Simple method based on amount and partner'),
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
            'date_base_on': fields.selection(
                [('newest', 'Most recent move line'),
                 ('actual', 'Today'),
                 ('end_period_last_credit', 'End of period of most recent credit'),
                 ('end_period', 'End of period of most recent move line'),
                 ('newest_credit', 'Date of most recent credit'),
                 ('newest_debit', 'Date of most recent debit')],
                 string='Date of reconcilation'),
            'filter': fields.char('Filter', size=128),
            'task_id': fields.many2one('account.easy.reconcile', 'Task', required=True, ondelete='cascade'),
    }

    _defaults = {
        'write_off': lambda *a: 0,
    }

    _order = 'sequence'

    def init(self, cr):
        """ Migration stuff, name is not anymore methods names
        but models name"""
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

class account_easy_reconcile(Model):

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

    def run_reconcile(self, cr, uid, ids, context=None):
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

                rec_model = self.pool.get(method.name)
                auto_rec_id = rec_model.create(
                    cr, uid, {'easy_reconcile_id': rec_id}, context=ctx)
                res = rec_model.automatic_reconcile(cr, uid, auto_rec_id, context=ctx)

                details += _(' method %d : %d lines |') % (count, res)
            log = self.read(cr, uid, rec_id, ['rec_log'], context=context)['rec_log']
            log_lines = log and log.splitlines() or []
            log_lines[0:0] = [_('%s : %d lines have been reconciled (%s)') %
                (time.strftime(DEFAULT_SERVER_DATETIME_FORMAT), total_rec, details[0:-2])]
            log = "\n".join(log_lines)
            self.write(cr, uid, rec_id, {'rec_log': log}, context=context)
        return True

