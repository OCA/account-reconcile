# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class MassReconcileBase(models.AbstractModel):
    _inherit = "mass.reconcile.base"

    def _reconcile_lines(self, lines, allow_partial=False):
        as_job = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("account.mass.reconcile.lines.as.job", default=False)
        )
        try:
            as_job = ast.literal_eval(as_job) if as_job else False
        except ValueError:
            as_job = False

        if as_job and self.env.context.get("reconcile_lines_as_job", True):
            wiz_data = self.copy_data()[0]
            self.with_delay().reconcile_lines_as_job(
                lines,
                allow_partial=allow_partial,
                wiz_creation_data=(self._name, wiz_data),
            )
            # Report is not available with reconcile jobs
            return False, False
        else:
            return super()._reconcile_lines(lines, allow_partial=allow_partial)

    @api.model
    def reconcile_lines_as_job(
        self, lines, allow_partial=False, wiz_creation_data=False
    ):
        new_wiz = self.env[wiz_creation_data[0]].create(wiz_creation_data[1])
        return new_wiz.with_context(reconcile_lines_as_job=False)._reconcile_lines(
            lines, allow_partial=allow_partial
        )
