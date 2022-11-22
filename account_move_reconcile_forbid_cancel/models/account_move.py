# Copyright 2022 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models, tools
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_receivable_payable_lines(self):
        return self.line_ids.filtered(
            lambda l: l.account_internal_type in ["receivable", "payable"],
        )

    def button_draft(self):
        if not self.env.context.get("skip_reconcile_forbid_cancel") and (
            not tools.config["test_enable"]
            or self.env.context.get("test_reconcile_forbid_cancel")
        ):
            rec_pay_lines = self._get_receivable_payable_lines()
            if rec_pay_lines.matched_debit_ids or rec_pay_lines.matched_credit_ids:
                raise ValidationError(
                    _("You cannot reset to draft reconciled entries.")
                )
        return super().button_draft()

    def button_cancel(self):
        if not self.env.context.get("skip_reconcile_forbid_cancel") and (
            not tools.config["test_enable"]
            or self.env.context.get("test_reconcile_forbid_cancel")
        ):
            rec_pay_lines = self._get_receivable_payable_lines()
            if rec_pay_lines.matched_debit_ids or rec_pay_lines.matched_credit_ids:
                raise ValidationError(_("You cannot cancel reconciled entries."))
        return super().button_cancel()
