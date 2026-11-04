# Copyright 2025 Simone Rubino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class ReconcileMultipleLines(models.TransientModel):
    _name = "account_reconcile_oca.reconcile_multiple_lines"
    _description = "Reconcile multiple lines with a reconciliation model"

    manual_model_id = fields.Many2one(
        comodel_name="account.reconcile.model",
        domain=[
            ("auto_reconcile", "=", False),
        ],
        required=True,
    )

    def _get_statement_lines(self):
        model = self.env.context.get("active_model")
        ids = self.env.context.get("active_ids")
        statement_lines = self.env[model].browse(ids)
        return statement_lines

    def _apply_model_to_line(self, reconciliation_model, statement_line):
        reconciliation_model.ensure_one()
        statement_line.ensure_one()
        partner = reconciliation_model._get_partner_from_mapping(statement_line)
        if not reconciliation_model._is_applicable_for(statement_line, partner):
            raise UserError(
                _(
                    "Reconcilation model %(model)s "
                    "cannot be applied to line %(line)s.\n"
                    "Please select a compatible reconciliation model "
                    "or deselect the line.",
                    model=reconciliation_model.display_name,
                    line=statement_line.display_name,
                )
            )
        statement_line.manual_model_id = reconciliation_model
        statement_line._onchange_manual_model_id()
        statement_line.reconcile_bank_line()

    def run(self):
        statement_lines = self._get_statement_lines()
        reconciliation_model = self.manual_model_id
        for line in statement_lines:
            self._apply_model_to_line(reconciliation_model, line)
