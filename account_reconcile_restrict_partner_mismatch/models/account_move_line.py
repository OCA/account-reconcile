# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import config


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def reconcile(self):
        if config["test_enable"] and not self.env.context.get("test_partner_mismatch"):
            return super().reconcile()

        # to be consistent with parent method
        if not self:
            return True
        partners = set()
        for line in self:
            if line.account_id.internal_type in ("receivable", "payable"):
                partners.add(line.partner_id.id)
        if len(partners) > 1:
            raise UserError(
                _(
                    "The partner has to be the same on all"
                    " lines for receivable and payable accounts!"
                )
            )
        return super().reconcile()
