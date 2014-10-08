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

from openerp.osv import orm, fields


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'transaction_id': fields.char(
            'Transaction ID',
            required=False,
            help="Transaction id from the financial institute"),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['transaction_id'] = False
        _super = super(SaleOrder, self)
        return _super.copy_data(cr, uid, id, default=default, context=context)

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """ Propagate the transaction_id from the sale order to the invoice """
        _super = super(SaleOrder, self)
        invoice_vals = _super._prepare_invoice(cr, uid, order, lines,
                                               context=context)
        invoice_vals['transaction_id'] = order.transaction_id
        return invoice_vals
