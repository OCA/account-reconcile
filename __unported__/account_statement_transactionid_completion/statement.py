# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume
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

from openerp.tools.translate import _
from openerp.osv.orm import Model
from openerp.osv import fields
from openerp.addons.account_statement_base_completion.statement import \
    ErrorTooManyPartner


class AccountStatementCompletionRule(Model):
    """Add a rule based on transaction ID"""

    _inherit = "account.statement.completion.rule"

    def _get_functions(self, cr, uid, context=None):
        res = super(AccountStatementCompletionRule, self)._get_functions(
            cr, uid, context=context)
        res += [
            ('get_from_transaction_id_and_so',
             'Match Sales Order using transaction ID'),
            ('get_from_transaction_id_and_invoice',
             'Match Invoice using transaction ID'),
        ]
        return res

    def get_from_transaction_id_and_so(self, cr, uid, st_line, context=None):
        """
        Match the partner based on the transaction ID field of the SO.
        Then, call the generic st_line method to complete other values.
        In that case, we always fullfill the reference of the line with the SO
        name.
        :param dict st_line: read of the concerned account.bank.statement.line
        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id' : value,
            ...}
            """
        st_obj = self.pool['account.bank.statement.line']
        res = {}
        so_obj = self.pool['sale.order']
        so_id = so_obj.search(
            cr, uid, [('transaction_id', '=', st_line['transaction_id'])],
            context=context)
        if len(so_id) > 1:
            raise ErrorTooManyPartner(
                _('Line named "%s" (Ref:%s) was matched by more than '
                  'one partner.') % (st_line['name'], st_line['ref']))
        if len(so_id) == 1:
            so = so_obj.browse(cr, uid, so_id[0], context=context)
            res['partner_id'] = so.partner_id.id
            res['ref'] = so.name
            st_vals = st_obj.get_values_for_line(
                cr, uid, profile_id=st_line['profile_id'],
                master_account_id=st_line['master_account_id'],
                partner_id=res.get('partner_id', False),
                line_type=st_line['type'],
                amount=st_line['amount'] if st_line['amount'] else 0.0,
                context=context)
            res.update(st_vals)
        return res

    def get_from_transaction_id_and_invoice(self, cr, uid, st_line,
                                            context=None):
        """Match the partner based on the transaction ID field of the invoice.
        Then, call the generic st_line method to complete other values.

        In that case, we always fullfill the reference of the line with the
        invoice name.

        :param dict st_line: read of the concerned account.bank.statement.line
        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id' : value,
            ...}
            """
        st_obj = self.pool['account.bank.statement.line']
        res = {}
        invoice_obj = self.pool['account.invoice']
        invoice_id = invoice_obj.search(
            cr, uid,
            [('transaction_id', '=', st_line['transaction_id'])],
            context=context)
        if len(invoice_id) > 1:
            raise ErrorTooManyPartner(
                _('Line named "%s" (Ref:%s) was matched by more than '
                  'one partner.') % (st_line['name'], st_line['ref']))
        elif len(invoice_id) == 1:
            invoice = invoice_obj.browse(cr, uid, invoice_id[0],
                                         context=context)
            res['partner_id'] = invoice.commercial_partner_id.id
            # we want the move to have the same ref than the found
            # invoice's move, thus it will be easier to link them for the
            # accountants
            if invoice.move_id:
                res['ref'] = invoice.move_id.ref
            st_vals = st_obj.get_values_for_line(
                cr, uid,
                profile_id=st_line['profile_id'],
                master_account_id=st_line['master_account_id'],
                partner_id=res.get('partner_id', False),
                line_type=st_line['type'],
                amount=st_line['amount'] if st_line['amount'] else 0.0,
                context=context)
            res.update(st_vals)
        return res


class AccountStatementLine(Model):
    _inherit = "account.bank.statement.line"

    _columns = {
        'transaction_id': fields.sparse(
            type='char', string='Transaction ID', size=128,
            serialization_field='additionnal_bank_fields',
            help="Transaction id from the financial institute"),
    }


class AccountBankStatement(Model):
    _inherit = "account.bank.statement"

    def _prepare_move_line_vals(
            self, cr, uid, st_line, move_id, debit, credit, currency_id=False,
            amount_currency=False, account_id=False, analytic_id=False,
            partner_id=False, context=None):
        """Add the period_id from the statement line date to the move
        preparation. Originaly, it was taken from the statement period_id

           :param browse_record st_line: account.bank.statement.line record to
             create the move from.
           :param int/long move_id: ID of the account.move to link the move
             line
           :param float debit: debit amount of the move line
           :param float credit: credit amount of the move line
           :param int/long currency_id: ID of currency of the move line to
             create
           :param float amount_currency: amount of the debit/credit expressed
             in the currency_id
           :param int/long account_id: ID of the account to use in the move
             line if different from the statement line account ID
           :param int/long analytic_id: ID of analytic account to put on the
             move line
           :param int/long partner_id: ID of the partner to put on the move
             line
           :return: dict of value to create() the account.move.line
        """
        res = super(AccountBankStatement, self)._prepare_move_line_vals(
            cr, uid, st_line, move_id, debit, credit,
            currency_id=currency_id,
            amount_currency=amount_currency,
            account_id=account_id,
            analytic_id=analytic_id,
            partner_id=partner_id, context=context)
        if st_line.transaction_id:
            res['transaction_ref'] = st_line.transaction_id
        return res
