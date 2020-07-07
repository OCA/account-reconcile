# Copyright 2019-2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    transaction_id = fields.Char(string='Transaction ID',
                                 index=True,
                                 copy=False,
                                 store=True,
                                 help="Transaction ID from the "
                                      "financial institute")

    @api.multi
    def _get_computed_reference(self):
        if self.transaction_id:
            return self.transaction_id
        return super()._get_computed_reference()
