# Copyright 2021 ForgeFlow
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    @api.constrains("matched_credit_ids", "matched_debit_ids", "parent_state")
    def _check_matched_state(self):
        params = self.env["ir.config_parameter"].sudo()
        allow_reconcile_only_posted = params.get_param(
            "account_reconcile_only_posted" ".allow_reconcile_only_posted",
            default=False,
        )
        if not allow_reconcile_only_posted:
            return True
        for rec in self.sudo():
            active_model = self.env.context.get("active_model")
            # During bank statement reconciliation the bank journal entry is
            # first created in draft, matched and then posted. Not like I
            # like that...
            if active_model == "account.bank.statement":
                continue
            mls = (
                rec.matched_credit_ids.mapped("credit_move_id")
                + rec.matched_debit_ids.mapped("debit_move_id")
                + rec
            )
            states = mls.mapped("parent_state")
            if len(mls) > 1 and (len(states) > 1 or (states and states[0] != "posted")):
                raise ValidationError(
                    _(
                        "Only posted journal items should be reconciled "
                        "together. In no other status it is allowed."
                    )
                )
