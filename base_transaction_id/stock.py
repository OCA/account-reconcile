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

from osv import osv

class StockPicking(osv.osv):
    _inherit = "stock.picking"

    def action_invoice_create(self, cursor, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        res = super(StockPicking, self).action_invoice_create(cursor, uid, ids,
            journal_id,group, type, context)
        for pick_id in res:
            pick =  self.browse(cursor, uid, pick_id)
            if pick.sale_id and pick.sale_id.transaction_id:
                self.pool.get('account.invoice').write(cursor,
                               uid,
                               res[pick_id],
                               {'transaction_id': pick.sale_id.transaction_id})
        return res
