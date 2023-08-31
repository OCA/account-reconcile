# Copyright 2022 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models, tools
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def button_draft(self):
        if not self.env.context.get("skip_reconcile_forbid_cancel") and (
            not tools.config["test_enable"]
            or self.env.context.get("test_reconcile_forbid_cancel")
        ):
            if self._get_reconciled_amls():
                raise ValidationError(
                    _("You cannot reset to draft reconciled entries.")
                )
        return super().button_draft()

    def button_cancel(self):
        if not self.env.context.get("skip_reconcile_forbid_cancel") and (
            not tools.config["test_enable"]
            or self.env.context.get("test_reconcile_forbid_cancel")
        ):
            if self._get_reconciled_amls():
                raise ValidationError(_("You cannot cancel reconciled entries."))
        return super().button_cancel()
