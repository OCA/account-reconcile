# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    transaction_id = fields.Char(
        'Transaction ID',
        required=False,
        copy=False,
        help="Transaction id from the financial institute"
    )

    @api.multi
    def _prepare_invoice(self):
        """Propagate the transaction_id from the sale order to the invoice."""
        invoice_vals = super()._prepare_invoice()
        invoice_vals['transaction_id'] = self.transaction_id
        return invoice_vals
