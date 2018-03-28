# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    transaction_id = fields.Char(
        'Transaction ID',
        required=False,
        copy=False,
        help="Transaction id from the financial institute"
    )

    invoice_ids = fields.Many2many(inverse='_inverse_invoice_ids')

    @api.multi
    def _get_liquidity_move_line_vals(self, amount):
        self.ensure_one()
        vals = super(AccountPayment, self)._get_liquidity_move_line_vals(
            amount)
        if self.transaction_id:
            vals['name'] = self.transaction_id
            vals['transaction_ref'] = self.transaction_id
        return vals

    @api.multi
    def _inverse_invoice_ids(self):
        for rec in self:
            invoices = rec.invoice_ids.filtered(lambda x: x.transaction_id)
            if not rec.transaction_id and invoices:
                rec.transaction_id = ", ".join(invoices.mapped(
                    'transaction_id'))
