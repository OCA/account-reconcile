# -*- coding: utf-8 -*-
"""Extend account.move.line to use date for period, when requested."""
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


class AccountMoveLine(orm.Model):
    """Extend account.move.line to use date for period, when requested."""
    _inherit = 'account.move.line'

    def create(self, cr, uid, vals, context=None, check=True):
        """If requested, override period from date."""
        ctx = context and context.copy() or {}
        if (('override_period_from_date' in ctx or
               'period_id' not in vals) and 'date' in vals):
            period_model = self.pool['account.period']
            search_date = 'date' in vals and vals['date'] or None
            period_ids = period_model.find(
                cr, uid, dt=search_date, context=ctx)
            if period_ids:
                vals['period_id'] = period_ids[0]
        return super(AccountMoveLine, self).create(
            cr, uid, vals, context=context, check=check)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
