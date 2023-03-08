# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class AccountPartialReconcile(models.Model):

    _inherit = "account.partial.reconcile"

    payment_mode_auto_reconcile = fields.Boolean()

    def create(self, vals):
        if self.env.context.get("_payment_mode_auto_reconcile"):
            for val in vals:
                val["payment_mode_auto_reconcile"] = True
        return super(AccountPartialReconcile, self).create(vals)
