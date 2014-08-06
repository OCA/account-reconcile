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
"""Wizard to Cancel a Statement."""

from openerp.osv import orm, fields


class wizard_cancel_statement(orm.TransientModel):

    """Wizard to Cancel a Statement."""

    _name = "wizard.cancel.statement"
    _description = "Cancel Statement"
    _columns = {
        'reconcile_warning': fields.boolean(
            'Show reconcile warning',
            help='This is a hidden field set with a default in the context '
            'to choose between two different warning messages in the view.'
        ),
    }

    def do_cancel_button(self, cr, uid, ids, context=None):
        """Proceed and cancel the statement, return Action.

        This will delete the move.line and the reconciliation.

        """
        return self.pool['account.bank.statement'].do_cancel(
            cr,
            uid,
            context['active_ids'],
            context=context
        )
