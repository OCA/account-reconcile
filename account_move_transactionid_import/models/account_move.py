# -*- coding: utf-8 -*-
# © 2011-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import _, fields, models
from openerp.addons.account_move_base_import.models.account_move import \
    ErrorTooManyPartner


class AccountMoveCompletionRule(models.Model):
    """Add a rule based on transaction ID"""

    _inherit = "account.move.completion.rule"

    function_to_call = fields.Selection(
        selection_add=[
            ('get_from_transaction_id_and_so',
             'Match Sales Order using transaction ID'),
            ('get_from_transaction_id_and_invoice',
             'Match Invoice using transaction ID')
        ])

    def get_from_transaction_id_and_so(self, line):
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

    def get_from_transaction_id_and_invoice(self, line):
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
            res['account_id'] = invoice.account_id.id
        return res
