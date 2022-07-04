# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import ast
import logging

from odoo import models

from odoo.addons.queue_job.job import identity_exact

_logger = logging.getLogger(__name__)


class AccountMassReconcile(models.Model):
    _inherit = "account.mass.reconcile"

    def run_reconcile(self):
        as_job = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("account.mass.reconcile.as.job", default=False)
        )
        try:
            as_job = ast.literal_eval(as_job) if as_job else False
        except ValueError:
            as_job = False

        if as_job and self.env.context.get("mass_reconcile_as_job", True):
            for rec in self:
                job_options = {"identity_key": identity_exact}
                rec.with_delay(**job_options).reconcile_as_job()
            return True
        else:
            return super().run_reconcile()

    def reconcile_as_job(self):
        """Run reconciliation on a single account"""
        return self.with_context(mass_reconcile_as_job=False).run_reconcile()
