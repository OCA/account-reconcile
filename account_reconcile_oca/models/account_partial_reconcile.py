# Copyright 2024 FactorLibre - Aritz Olea
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountPartialReconcile(models.Model):

    _inherit = "account.partial.reconcile"

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get("no_credit_currency", False):
            for vals in vals_list:
                vals["credit_amount_currency"] = 0
        elif self.env.context.get("no_debit_currency", False):
            for vals in vals_list:
                vals["debit_amount_currency"] = 0
        return super().create(vals_list)
