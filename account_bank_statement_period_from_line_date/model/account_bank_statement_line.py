# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Therp BV - http://therp.nl.
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
from openerp import models, api


class AccountBankStatementLine(models.Model):
    """Extend account.bank.statement.line to use transaction date in moves."""
    _inherit = 'account.bank.statement.line'

    @api.one
    def process_reconciliation(self, mv_line_dicts):
        """ Retrieve the period derived from the statement line and store in
        the context for further use """
        periods = self.env['account.period'].find(dt=self.date)
        if periods:
            return super(AccountBankStatementLine,
                         self.with_context(force_period_id=periods[0].id)).\
                process_reconciliation(mv_line_dicts)
        return super(AccountBankStatementLine, self).process_reconciliation(
            mv_line_dicts)
