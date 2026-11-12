# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import config
from odoo.tools.misc import formatLang


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def reconcile(self):
        if config["test_enable"] and not self.env.context.get("test_partner_mismatch"):
            return super().reconcile()

        # to be consistent with parent method
        if not self:
            return True
        rp_lines = self.filtered(
            lambda line: line.account_id.internal_type in ("receivable", "payable")
        )
        if len(set(rp_lines.mapped(lambda line: line.partner_id.id))) > 1:
            details = "\n".join(
                "- %s | %s | %s | %s"
                % (
                    line.move_id.display_name,
                    line.account_id.code,
                    line.partner_id.display_name or _("No partner"),
                    formatLang(
                        self.env, line.balance, currency_obj=line.company_currency_id
                    ),
                )
                for line in rp_lines.sorted(lambda line: line.partner_id.id or 0)
            )
            raise UserError(
                _(
                    "Reconciliation impossible: the partner must be the same on all "
                    "receivable and payable lines.\n\n"
                    "Lines involved (entry | account | partner | balance):\n%s\n\n"
                    "To fix it, set the same partner on these entries (invoice, "
                    "payment or journal entry), then retry."
                )
                % details
            )
        return super().reconcile()
