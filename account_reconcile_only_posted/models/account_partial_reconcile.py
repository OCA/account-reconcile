# Copyright 2021 ForgeFlow
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountPartialReconcile(models.Model):

    _inherit = "account.partial.reconcile"

    @api.constrains("credit_move_id", "debit_move_id")
    def _check_debit_credit_state(self):
        params = self.env["ir.config_parameter"].sudo()
        allow_reconcile_only_posted = params.get_param(
            "account_reconcile_only_posted" ".allow_reconcile_only_posted",
            default=False,
        )
        if not allow_reconcile_only_posted:
            return True
        for rec in self.sudo():
            cr_move = rec.credit_move_id.move_id
            dr_move = rec.debit_move_id.move_id
            active_model = self.env.context.get("active_model")
            if active_model == "account.bank.statement":
                return True
            if dr_move.state != "posted" or cr_move.state != "posted":
                raise ValidationError(
                    _(
                        "It is only possible to match posted journal entries. "
                        "Journal entry %s is in status %s, and Journal Entry "
                        "%s is in status %s"
                    )
                    % (cr_move.name, cr_move.state, dr_move.name, dr_move.state)
                )
