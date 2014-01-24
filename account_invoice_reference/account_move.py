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

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        # invoice from which the move is generated
        invoice = context.get('invoice')
        if invoice:
            assert isinstance(invoice, orm.browse_record)
            invoice_obj = self.pool['account.invoice']
            ref = invoice_obj._ref_from_invoice(cr, uid, invoice, context=context)
            vals = vals.copy()
            vals['ref'] = ref
        move_id = super(account_move, self).\
            create(cr, uid, vals, context=context)
        return move_id


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def _ref_from_invoice(self, cr, uid, invoice, context=None):
        if invoice.type in ('out_invoice', 'out_refund'):
            return invoice.origin
        elif invoice.type in ('in_invoice', 'in_refund'):
            return invoice.supplier_invoice_number

    def action_number(self, cr, uid, ids, context=None):
        # force the number of the invoice to be updated for the
        # subsequent browse
        self.write(cr, uid, ids, {})

        for invoice in self.browse(cr, uid, ids, context=context):
            ref = self._ref_from_invoice(cr, uid, invoice, context=context)
            if not ref:
                ref = invoice.number
            move_id = invoice.move_id.id if invoice.move_id else False

            self.write(cr, uid, ids, {'internal_number': invoice.number},
                       context=context)
            cr.execute('UPDATE account_move SET ref=%s '
                       'WHERE id=%s AND (ref is null OR ref = \'\')',
                       (ref, move_id))
            cr.execute('UPDATE account_move_line SET ref=%s '
                       'WHERE move_id=%s AND (ref is null OR ref = \'\')',
                       (ref, move_id))
            cr.execute('UPDATE account_analytic_line SET ref=%s '
                       'FROM account_move_line '
                       'WHERE account_move_line.move_id = %s '
                       'AND account_analytic_line.move_id = account_move_line.id',
                       (ref, move_id))
        return True

    def create(self, cr, uid, vals, context=None):
        if (vals.get('supplier_invoice_reference') and not
                vals.get('reference')):
            vals['reference'] = vals['supplier_invoice_reference']
        return super(account_invoice, self).create(cr, uid, vals,
                                                   context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('supplier_invoice_reference'):
            if isinstance(ids, (int, long)):
                ids = [ids]
            for invoice in self.browse(cr, uid, ids, context=context):
                local_vals = vals
                if not invoice.reference:
                    locvals = vals.copy()
                    locvals['reference'] = vals['supplier_invoice_reference']
            return super(account_invoice, self).write(cr, uid, [invoice.id],
                                                      locvals, context=context)
        else:
            return super(account_invoice, self).write(cr, uid, ids, vals,
                                                      context=context)
