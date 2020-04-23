# Copyright 2017-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_open_reconcile(self):
        # Open reconciliation view for customers and suppliers
        reconcile_mode = self.env.context.get("reconcile_mode", False)
        accounts = self.property_account_payable_id
        if reconcile_mode == "customers":
            accounts = self.property_account_receivable_id

        action_context = {
            "show_mode_selector": True,
            "partner_ids": [self.id],
            "mode": reconcile_mode,
            "account_ids": accounts.ids,
        }
        return {
            "type": "ir.actions.client",
            "tag": "manual_reconciliation_view",
            "context": action_context,
        }
