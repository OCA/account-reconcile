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
"""Wizard to Cancel a Statement Line."""

from openerp.osv import orm


class wizard_cancel_statement_line(orm.TransientModel):

    """Wizard to Cancel a Statement Line."""

    _name = "wizard.cancel.statement.line"
    _description = "Cancel Statement Line"
    _columns = {
    }

    def unreconcile(self, cr, uid, ids, context=None):
        """Proceed and cancel the statement line, return Action.

        This will delete the move.line and the reconciliation.

        """
        return self.pool['account.bank.statement.line'].cancel(
            cr,
            uid,
            context['active_ids'],
            context=context
        )
