# -*- coding: utf-8 -*-
# © 2011-2012 Nicolas Bessi (Camptocamp)
# © 2012-2015 Yannick Vaucher (Camptocamp)
from openerp import models, fields, api


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
        """ Propagate the transaction_id from the sale order to the invoice """
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['transaction_id'] = self.transaction_id
        return invoice_vals
