# Copyright 2019-2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    transaction_id = fields.Char(
        string="Transaction ID",
        index=True,
        copy=False,
        store=True,
        help="Transaction ID from the financial institute",
    )

    def _get_invoice_reference_odoo_invoice(self):
        if self.transaction_id:
            return self.transaction_id
        return super()._get_invoice_reference_odoo_invoice()
