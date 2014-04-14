# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2013 Camptocamp SA (http://www.camptocamp.com)
#   @author Nicolas Bessi
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

import time


class AccountStatementFromInvoiceLines(orm.TransientModel):

    _inherit = "account.statement.from.invoice.lines"

    def populate_statement(self, cr, uid, ids, context=None):
        """Taken from account voucher as no hook is available. No function
        no refactoring, just trimming the part that generates voucher"""
        if context is None:
            context = {}
        statement_id = context.get('statement_id', False)
        if not statement_id:
            return {'type': 'ir.actions.act_window_close'}
        data = self.read(cr, uid, ids, context=context)[0]
        line_ids = data['line_ids']
        if not line_ids:
            return {'type': 'ir.actions.act_window_close'}

        line_obj = self.pool.get('account.move.line')
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        currency_obj = self.pool.get('res.currency')
        line_date = time.strftime('%Y-%m-%d')
        statement = statement_obj.browse(cr, uid, statement_id, context=context)
        # for each selected move lines
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            ctx = context.copy()
            #  take the date for computation of currency => use payment date
            ctx['date'] = line_date
            amount = 0.0

            if line.debit > 0:
                amount = line.debit
            elif line.credit > 0:
                amount = -line.credit

            if line.amount_currency:
                amount = currency_obj.compute(cr, uid, line.currency_id.id,
                    statement.currency.id, line.amount_currency, context=ctx)
            elif (line.invoice and line.invoice.currency_id.id != statement.currency.id):
                amount = currency_obj.compute(cr, uid, line.invoice.currency_id.id,
                    statement.currency.id, amount, context=ctx)

            context.update({'move_line_ids': [line.id],
                            'invoice_id': line.invoice.id})
            s_type = 'general'
            if line.journal_id.type in ('sale', 'sale_refund'):
                s_type = 'customer'
            elif line.journal_id.type in ('purchase', 'purhcase_refund'):
                s_type = 'supplier'
            vals = self._prepare_statement_line_vals(
                cr, uid, line, s_type, statement_id, amount, context=context)
            statement_line_obj.create(cr, uid, vals, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def _prepare_statement_line_vals(self, cr, uid, move_line, s_type,
                                     statement_id, amount, context=None):
        return {'name': move_line.name or '?',
                'amount': amount,
                'type': s_type,
                'partner_id': move_line.partner_id.id,
                'account_id': move_line.account_id.id,
                'statement_id': statement_id,
                'ref': move_line.ref,
                'voucher_id': False,
                'date': time.strftime('%Y-%m-%d'),
                }


class AccountPaymentPopulateStatement(orm.TransientModel):
    _inherit = "account.payment.populate.statement"

    def populate_statement(self, cr, uid, ids, context=None):
        """Taken from payment addon as no hook is vailable. No function
        no refactoring, just trimming the part that generates voucher"""
        line_obj = self.pool.get('payment.line')
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        currency_obj = self.pool.get('res.currency')

        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        line_ids = data['lines']
        if not line_ids:
            return {'type': 'ir.actions.act_window_close'}

        statement = statement_obj.browse(cr, uid, context['active_id'], context=context)

        for line in line_obj.browse(cr, uid, line_ids, context=context):
            ctx = context.copy()
            ctx['date'] = line.ml_maturity_date  # Last value_date earlier,but this field exists no more now
            amount = currency_obj.compute(cr, uid, line.currency.id,
                    statement.currency.id, line.amount_currency, context=ctx)
            if not line.move_line_id.id:
                continue
            context.update({'move_line_ids': [line.move_line_id.id]})
            vals = self._prepare_statement_line_vals(
                cr, uid, line, -amount, statement, context=context)
            st_line_id = statement_line_obj.create(cr, uid, vals,
                                                   context=context)

            line_obj.write(cr, uid, [line.id], {'bank_statement_line_id': st_line_id})
        return {'type': 'ir.actions.act_window_close'}

    def _prepare_statement_line_vals(self, cr, uid, payment_line, amount,
                                     statement, context=None):
        return {'name': payment_line.order_id.reference or '?',
                'amount': amount,
                'type': 'supplier',
                'partner_id': payment_line.partner_id.id,
                'account_id': payment_line.move_line_id.account_id.id,
                'statement_id': statement.id,
                'ref': payment_line.communication,
                'date': (payment_line.date or payment_line.ml_maturity_date or
                         statement.date)
                }
