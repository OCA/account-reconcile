# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    transaction_id = fields.Char(string='Transaction ID',
                                 index=True,
                                 copy=False,
                                 help="Transaction ID from the "
                                      "financial institute")

    @api.multi
    def action_move_create(self):
        """Propagate the transaction_id from the invoice to the move ref."""
        res = super().action_move_create()
        for invoice in self:
            if invoice.transaction_id:
                invoice.move_id.ref = invoice.transaction_id
        return res
