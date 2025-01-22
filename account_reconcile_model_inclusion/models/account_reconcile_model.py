# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"

    include_reconcile_model_ids = fields.Many2many(
        comodel_name="account.reconcile.model",
        relation="account_reconcile_model_include_rel",
        column1="model_id",
        column2="included_model_id",
    )
    exclude_reconcile_model_ids = fields.Many2many(
        comodel_name="account.reconcile.model",
        relation="account_reconcile_model_exclude_rel",
        column1="model_id",
        column2="excluded_model_id",
    )

    def _account_reconcile_model_inclusion_expression(self, seen=None):
        """
        Build an expression with 'm{model.id}' as variables that expresses
        the applicability of a model recursively wrt includes/excludes
        """
        seen = seen or set()
        seen.add(self)
        result = (
            f"(m{self.id} and "
            + (
                " and ".join(
                    include._account_reconcile_model_inclusion_expression(seen.copy())
                    if include not in seen
                    else f"m{include.id}"
                    for include in self.include_reconcile_model_ids
                )
                or "True"
            )
            + " and "
            + (
                " and ".join(
                    "not "
                    + exclude._account_reconcile_model_inclusion_expression(seen.copy())
                    if exclude not in seen
                    else f"m{exclude.id}"
                    for exclude in self.exclude_reconcile_model_ids
                )
                or "True"
            )
            + ")"
        )
        return result

    def _is_applicable_for(self, st_line, partner):
        """
        Apply inclusion/exclusion of other models' results
        """
        result = super()._is_applicable_for(st_line, partner)

        if not result or self.env.context.get("account_reconcile_model_inclusion"):
            return result

        expression = self._account_reconcile_model_inclusion_expression()
        eval_context = {
            f"m{model.id}": model._is_applicable_for(st_line, partner)
            for model in self.search([]).with_context(
                account_reconcile_model_inclusion=True
            )
        }
        return safe_eval(expression, eval_context)
