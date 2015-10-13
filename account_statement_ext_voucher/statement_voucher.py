# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume
#    Copyright 2011-2012 Camptocamp SA
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

from openerp.osv.orm import Model


class AccountVoucher(Model):

    _inherit = 'account.voucher'

    def _get_period(self, cr, uid, context=None):
        """If period not in context, take it from the move lines"""
        if context is None:
            context = {}
        if not context.get('period_id') and context.get('move_line_ids'):
            res = self.pool.get('account.move.line').browse(
                cr, uid, context.get('move_line_ids'),
                context=context)[0].period_id.id
            context['period_id'] = res
        elif context.get('date'):
            periods = self.pool['account.period'].find(
                cr, uid, dt=context['date'], context=context)
            if periods:
                context['period_id'] = periods[0]
        return super(AccountVoucher, self)._get_period(cr, uid, context)

    def create(self, cr, uid, values, context=None):
        """If no period defined in values, ask it from moves."""
        if context is None:
            context = {}
        if not values.get('period_id'):
            ctx = dict(context, date=values.get('date'))
            values['period_id'] = self._get_period(cr, uid, ctx)
        return super(AccountVoucher, self).create(cr, uid, values, context)
