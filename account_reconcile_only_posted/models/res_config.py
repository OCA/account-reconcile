# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    allow_reconcile_only_posted = fields.Boolean(
        string="Allow reconciliations only between posted entries",
        help="When set, it won't be possible to reconcile journal entries if "
        "if any of them is not posted.",
    )

    @api.model
    def get_values(self):
        res = super(AccountConfigSettings, self).get_values()
        params = self.env["ir.config_parameter"].sudo()
        res.update(
            allow_reconcile_only_posted=bool(
                params.get_param(
                    "account_reconcile_only_posted" ".allow_reconcile_only_posted",
                    default=False,
                )
            )
        )
        return res

    def set_values(self):
        super(AccountConfigSettings, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "account_reconcile_only_posted.allow_reconcile_only_posted",
            self.allow_reconcile_only_posted,
        )
