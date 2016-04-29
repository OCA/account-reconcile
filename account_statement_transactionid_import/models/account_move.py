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

from openerp import _, models
from openerp.addons.account_statement_base_import.models.account_move import \
    ErrorTooManyPartner


class AccountMoveCompletionRule(models.Model):
    """Add a rule based on transaction ID"""

    _inherit = "account.move.completion.rule"

    def _get_functions(self):
        res = super(AccountMoveCompletionRule, self)._get_functions()
        res += [
            ('get_from_transaction_ref_and_so',
             'Match Sales Order using transaction ref'),
            ('get_from_transaction_ref_and_invoice',
             'Match Invoice using transaction ref'),
        ]
        return res

    def get_from_transaction_ref_and_so(self, line):
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
        res = {}
        so_obj = self.env['sale.order']
        sales = so_obj.search([('transaction_id', '=', line.transaction_ref)])
        if len(sales) > 1:
            raise ErrorTooManyPartner(
                _('Line named "%s" was matched by more than '
                  'one partner.') % line.name)
        if len(sales) == 1:
            sale = sales[0]
            res['partner_id'] = sale.partner_id.id
        return res

    def get_from_transaction_ref_and_invoice(self, line):
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
        res = {}
        invoice_obj = self.env['account.invoice']
        invoices = invoice_obj.search(
            [('transaction_id', '=', line.transaction_ref)])
        if len(invoices) > 1:
            raise ErrorTooManyPartner(
                _('Line named "%s" was matched by more than '
                  'one partner.') % line.name)
        elif len(invoices) == 1:
            invoice = invoices[0]
            res['partner_id'] = invoice.commercial_partner_id.id
        return res
