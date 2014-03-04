# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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


class AccountPaymentPopulateStatement(orm.TransientModel):
    _inherit = "account.payment.populate.statement"

    def _prepare_statement_line_vals(self, cr, uid, payment_line, amount,
                                     statement, context=None):
        superself = super(AccountPaymentPopulateStatement, self)
        vals = superself._prepare_statement_line_vals(
            cr, uid, payment_line, amount, statement, context=context)
        if payment_line.move_line_id:
            vals['transaction_id'] = payment_line.move_line_id.transaction_ref
        return vals


class account_statement_from_invoice_lines(orm.TransientModel):
    _inherit = "account.statement.from.invoice.lines"

    def _prepare_statement_line_vals(self, cr, uid, move_line, s_type,
                                     statement_id, amount, context=None):
        superself = super(account_statement_from_invoice_lines, self)
        vals = superself._prepare_statement_line_vals(
            cr, uid, move_line, s_type, statement_id, amount, context=context)
        vals['transaction_id'] = move_line.transaction_ref
        return vals
