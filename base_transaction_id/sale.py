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

from osv import fields, osv

class SaleOrder(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'transaction_id':fields.char('Transaction id', size=128,required=False,
                                     help="Transction id from the financial institute"),
    }


    def _prepare_invoice(self, cursor, uid, order, lines, context=None):
        #we put the transaction id in the generated invoices
        if context is None:
            context = {}
        invoice_vals = super(SaleOrder, self)._prepare_invoice(cursor, uid, order, lines, context)
        invoice_vals.update({
            'transaction_id': order.transaction_id})
        return invoice_vals
