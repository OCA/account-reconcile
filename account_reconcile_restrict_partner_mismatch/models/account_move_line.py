# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @property
    def _check_partner_mismatch_on_reconcile(self):
        """
        Returns True if the partner mismatch check on reconcile should be done
        """
        self.ensure_one()
        return bool(
            self.company_id.restrict_partner_mismatch_on_reconcile
            and not self.journal_id.no_restrict_partner_mismatch_on_reconcile
            and self.account_id.account_type
            in ("asset_receivable", "liability_payable")
        )

    def reconcile(self):
        # to be consistent with parent method
        if self:
            partners = set()
            for line in self:
                if line._check_partner_mismatch_on_reconcile:
                    partners.add(line.partner_id.id)
            if len(partners) > 1:
                raise UserError(
                    _(
                        "The partner has to be the same on all"
                        " lines for receivable and payable accounts!"
                    )
                )
        return super().reconcile()
