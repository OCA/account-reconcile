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


class AccountMoveLine(models.Model):
    """Extend account.move.line to use date for period, when requested."""
    _inherit = 'account.move.line'

    @api.model
    def create(self, vals, check=True):
        """If requested, override period from date."""
        if self.env.context.get('force_period_id'):
            vals['period_id'] = self.env.context['force_period_id']
        return super(AccountMoveLine, self).create(vals, check=check)
