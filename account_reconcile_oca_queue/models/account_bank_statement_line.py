# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

from odoo.addons.queue_job.job import identity_exact


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def _register_hook(self):
        method = "_do_auto_reconcile"
        self._patch_method(
            method,
            self._patch_job_auto_delay(
                method, context_key="auto_delay_do_auto_reconcile"
            ),
        )
        return super()._register_hook()

    def _do_auto_reconcile_job_options(self, models):
        return {
            "description": self.env._(
                "Auto reconcile %(label)s", label=self.payment_ref
            ),
            "identity_key": identity_exact,
        }

    def _auto_reconcile(self):
        if self.company_id.account_auto_reconcile_queue:
            self = self.with_context(auto_delay_do_auto_reconcile=True)
        return super()._auto_reconcile()
