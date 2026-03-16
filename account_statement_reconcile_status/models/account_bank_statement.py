# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    reconcile_state = fields.Selection(
        selection=[
            ("not_started", "Not Started"),
            ("in_progress", "In Progress"),
            ("done", "Fully Reconciled"),
        ],
        string="Reconciliation Status",
        compute="_compute_reconcile_state",
        store=True,
    )
    date_first_fully_reconciled = fields.Datetime(
        string="First Fully Reconciled On",
        readonly=True,
        copy=False,
    )

    @api.depends("line_ids.is_reconciled", "line_ids.state")
    def _compute_reconcile_state(self):
        for stmt in self:
            posted_lines = stmt.line_ids.filtered(lambda line: line.state == "posted")
            total = len(posted_lines)
            reconciled = len(posted_lines.filtered("is_reconciled"))
            if total and reconciled == total:
                stmt.reconcile_state = "done"
            elif reconciled > 0:
                stmt.reconcile_state = "in_progress"
            else:
                stmt.reconcile_state = "not_started"

    @api.constrains("reconcile_state")
    def _set_date_first_fully_reconciled(self):
        newly_done = self.filtered(
            lambda s: s.reconcile_state == "done" and not s.date_first_fully_reconciled
        )
        if newly_done:
            newly_done.write({"date_first_fully_reconciled": fields.Datetime.now()})
