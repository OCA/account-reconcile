# -*- coding: utf-8 -*-
"""Extend account.bank.statement.line to use transaction date in moves."""
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


class AccountBankStatementLine(orm.Model):
    """Extend account.bank.statement.line to use transaction date in moves."""
    _inherit = 'account.bank.statement.line'

    def process_reconciliation(
            self, cr, uid, id, mv_line_dicts, context=None):
        """Put marker in context to use period from date in move line."""
        ctx = context.copy() or {}
        ctx['override_period_from_date'] = True
        return super(AccountBankStatementLine, self).process_reconciliation(
            cr, uid, id, mv_line_dicts, context=ctx)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
