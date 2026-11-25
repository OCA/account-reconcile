# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    transaction_id = fields.Char(
        string="Transaction ID",
        index=True,
        copy=False,
        help="Transaction ID from the financial institute",
    )
