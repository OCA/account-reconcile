# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class AccountMassReconcile(models.Model):
    _inherit = "account.mass.reconcile"

    is_cron_executed = fields.Boolean("Cron execution?")

    def reconcile_as_cron(self):
        records = self.env["account.mass.reconcile"].search(
            [("is_cron_executed", "=", True)]
        )
        for rec in records:
            rec.run_reconcile()
