# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Author: Leonardo Pistone
#   Copyright 2014 Camptocamp SA
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################
"""Account Statement Cancel Line."""

from openerp.osv import orm


class Statement(orm.Model):

    """Bank Statement.

    Minimal changes to allow cancelling single lines.

    """

    _inherit = "account.bank.statement"

    _columns = {
    }

    _defaults = {
    }

    def button_confirm_bank(self, cr, uid, ids, context=None):
        """Change the state on the statement lines. Return super."""
        st_line_obj = self.pool['account.bank.statement.line']
        for st_data in self.read(cr, uid, ids, ['line_ids'], context=context):
            st_line_obj.write(cr, uid, st_data['line_ids'], {
                'state': 'confirmed'
            }, context=context)

        return super(Statement, self).button_confirm_bank(
            cr, uid, ids, context)

    def button_cancel(self, cr, uid, ids, context=None):
        """Change the state on the statement lines. Return super."""
        st_line_obj = self.pool['account.bank.statement.line']
        for st_data in self.read(cr, uid, ids, ['line_ids'], context=context):
            st_line_obj.write(cr, uid, st_data['line_ids'], {
                'state': 'draft'
            }, context=context)

        return super(Statement, self).button_cancel(
            cr, uid, ids, context)
