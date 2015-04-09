# -*- coding: utf-8 -*-
"""Extend account.bank.statement to use transaction date in moves."""
##############################################################################
#
#    Copyright (C) 2015 Therp BV - http://therp.nl.
#    All Rights Reserved
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


class AccountBankStatement(orm.Model):
    """Extend account.bank.statement to use transaction date in moves."""
    _inherit = 'account.bank.statement'

    def _prepare_move(
            self, cr, uid, st_line, st_line_number, context=None):
        """Put marker in context to use period from date in move line."""
        res = super(AccountBankStatement, self)._prepare_move(
            cr, uid, st_line, st_line_number, context=context)
        context = context or {}
        if (('override_period_from_date' in context or
               'period_id' not in res) and 'date' in res):
            period_model = self.pool['account.period']
            search_date = 'date' in res and res['date'] or None
            period_ids = period_model.find(
                cr, uid, dt=search_date, context=context)
            if period_ids:
                res['period_id'] = period_ids[0]
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
