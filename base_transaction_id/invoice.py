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
