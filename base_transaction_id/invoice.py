# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2011-2012 Camptocamp SA
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

from openerp.osv.orm import Model
from openerp.osv import fields


class AccountInvoice(Model):
    _inherit = 'account.invoice'

    _columns = {
        'transaction_id': fields.char(
            'Transaction id',
            select=1,
            help="Transaction id from the financial institute"),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['transaction_id'] = False
        return super(AccountInvoice, self).\
            copy_data(cr, uid, id, default=default, context=context)

    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        if invoice_browse.transaction_id:
            invoice_account_id = invoice_browse.account_id.id
            for line in move_lines:
                # tuple (0, 0, {values})
                if invoice_account_id == line[2]['account_id']:
                    line[2]['transaction_ref'] = invoice_browse.transaction_id
        return move_lines
