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


class AccountBankStatement(models.Model):
    """Extend account.bank.statement to use transaction date in moves."""
    _inherit = 'account.bank.statement'

    @api.model
    def _prepare_move(self, st_line, st_line_number):
        """If requested, override period from date."""
        res = super(AccountBankStatement, self)._prepare_move(
            st_line, st_line_number)
        if self.env.context.get('force_period_id'):
            res['period_id'] = self.env.context['force_period_id']
        return res
