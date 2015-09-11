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

from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.v8
    def _ref_from_invoice(self):
        self.ensure_one()

        def preferred_ref():
            if self.type in ('out_invoice', 'out_refund'):
                return self.origin
            elif self.type in ('in_invoice', 'in_refund'):
                return self.supplier_invoice_number
            else:
                return None

        return preferred_ref() or self.number

    @api.v7
    def _ref_from_invoice(self, cr, uid, invoice, context=None):
        return invoice._ref_from_invoice()

    @api.multi
    def action_number(self):
        # force the number of the invoice to be updated for the
        # subsequent browse
        self.write({})

        for invoice in self:
            ref = invoice._ref_from_invoice()
            move_id = invoice.move_id.id if invoice.move_id else False

            invoice.write({'internal_number': invoice.number})

            cr = self._cr
            cr.execute("UPDATE account_move SET ref=%s "
                       "WHERE id=%s AND (ref is null OR ref = '')",
                       (ref, move_id))
            cr.execute("UPDATE account_move_line SET ref=%s "
                       "WHERE move_id=%s AND (ref is null OR ref = '')",
                       (ref, move_id))
            cr.execute(
                "UPDATE account_analytic_line SET ref=%s "
                "FROM account_move_line "
                "WHERE account_move_line.move_id = %s "
                "AND account_analytic_line.move_id = account_move_line.id",
                (ref, move_id))
            self.invalidate_cache()
        return True

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        if (vals.get('supplier_invoice_number') and not
                vals.get('reference')):
            vals = vals.copy()
            vals['reference'] = vals['supplier_invoice_number']
        return super(AccountInvoice, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('supplier_invoice_number'):
            for invoice in self:
                loc_vals = None
                if not invoice.reference:
                    loc_vals = vals.copy()
                    loc_vals['reference'] = vals['supplier_invoice_number']
                super(AccountInvoice, invoice).write(loc_vals or vals)
            return True
        else:
            return super(AccountInvoice, self).write(vals)
