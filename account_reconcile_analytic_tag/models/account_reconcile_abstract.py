# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class AccountReconcileAbstract(models.AbstractModel):
    _inherit = "account.reconcile.abstract"

    def _get_reconcile_line(
        self, line, kind, is_counterpart=False, max_amount=False, from_unreconcile=False
    ):
        vals = super()._get_reconcile_line(
            line=line,
            kind=kind,
            is_counterpart=is_counterpart,
            max_amount=max_amount,
            from_unreconcile=from_unreconcile,
        )
        vals[0]["manual_analytic_tag_ids"] = [(6, 0, line.analytic_tag_ids.ids)]
        return vals
