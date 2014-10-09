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

from openerp.osv import orm


class StockPicking(orm.Model):
    _inherit = "stock.picking"

    def _create_invoice_from_picking(self, cr, uid, picking, vals,
                                     context=None):
        """ Propagate the transaction ID from sale to invoice """
        vals['transaction_id'] = picking.sale_id.transaction_id
        _super = super(StockPicking, self)
        return _super._create_invoice_from_picking(cr, uid, picking, vals,
                                                   context=context)
