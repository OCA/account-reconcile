# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Romain Deheele
#    Copyright 2013 Camptocamp SA
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

from openerp.osv.orm import Model, fields

class AccountMoveLine(Model):
    """
    Inherit account.move.line class in order to add transaction_ref field
    """
    _inherit = "account.move.line"
    _columns = {
        'transaction_ref': fields.char('Transaction Ref.', size=128),
    }
    
class AccountBankSatement(Model):
    """
    Inherit account.bank.statement class in order to set transaction_ref info on account.move.line
    """
    _inherit = "account.bank.statement"   
   
    def _prepare_move_line_vals(
            self, cr, uid, st_line, move_id, debit, credit, currency_id=False,
            amount_currency=False, account_id=False, analytic_id=False,
            partner_id=False, context=None):

        if context is None:
            context = {}
        res = super(AccountBankSatement, self)._prepare_move_line_vals(
                cr, uid, st_line, move_id, debit, credit,
                currency_id=currency_id,
                amount_currency=amount_currency,
                account_id=account_id,
                analytic_id=analytic_id,
                partner_id=partner_id, context=context)
        res.update({'transaction_ref': st_line.ref})
        return res
