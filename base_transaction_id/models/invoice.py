# -*- coding: utf-8 -*-
# © 2011-2012 Nicolas Bessi (Camptocamp)
# © 2012-2015 Yannick Vaucher (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    transaction_id = fields.Char(string='Transaction ID',
                                 index=True,
                                 copy=False,
                                 help="Transaction ID from the "
                                      "financial institute")

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        """ Propagate the transaction_id from the invoice to the move lines.

        The transaction id is written on the move lines only if the account is
        the same than the invoice's one.
        """
        move_lines = super(AccountInvoice, self).finalize_invoice_move_lines(
            move_lines)
        for invoice in self:
            if invoice.transaction_id:
                invoice_account_id = invoice.account_id.id
                for line in move_lines:
                    # line is a tuple (0, 0, {values})
                    if invoice_account_id == line[2]['account_id']:
                        line[2]['transaction_ref'] = invoice.transaction_id
        return move_lines
