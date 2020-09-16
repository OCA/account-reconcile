# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools.misc import formatLang


class AccountReconciliation(models.AbstractModel):
    _inherit = "account.reconciliation.widget"

    @api.model
    def _get_statement_line(self, st_line):
        res = super()._get_statement_line(st_line)

        res.update({
            "ignore_currency": st_line.ignore_currency,
            "original_amount_currency": st_line.original_amount_currency,
            "original_amount_currency_str": (
                st_line.original_currency_id and formatLang(
                    self.env,
                    abs(st_line.original_amount_currency),
                    currency_obj=st_line.original_currency_id,
                ) or ""
            ),
            "original_currency_id": st_line.original_currency_id.id,
        })

        return res
