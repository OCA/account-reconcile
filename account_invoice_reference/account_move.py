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

from openerp.osv import orm, fields


class account_move(orm.Model):
    _inherit = 'account.move'

    def _ref_from_invoice(self, cr, uid, invoice, context=None):
        if invoice.type == 'out_invoice':
            return invoice.origin or invoice.name
        elif invoice.type == 'in_invoice':
            # the supplier invoice number is now mandatory, but
            # if historical invoices should not have one, we fallback
            # to the name of the invoice
            return invoice.supplier_invoice_number or invoice.name

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        # invoice from which the move is generated
        invoice = context.get('invoice')
        if invoice:
            assert isinstance(invoice, orm.browse_record)
            ref = self._ref_from_invoice(cr, uid, invoice, context=context)
            if ref:
                vals = vals.copy()
                vals['ref'] = ref
        move_id = super(account_move, self).\
            create(cr, uid, vals, context=context)
        return move_id
