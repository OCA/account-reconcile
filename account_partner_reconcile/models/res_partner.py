# Copyright 2017-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_open_reconcile(self):
        # Open reconciliation view for customers and suppliers
        self.ensure_one()

        reconcile_mode = self.env.context.get("reconcile_mode", False)
        account = self.property_account_payable_id
        if reconcile_mode == "customers":
            account = self.property_account_receivable_id

        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_reconcile_oca.account_account_reconcile_act_window"
        )

        action["domain"] = [
            ("account_id", "=", account.id),
            ("partner_id", "=", self.id),
        ]

        return action
