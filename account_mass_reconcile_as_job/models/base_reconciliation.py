# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MassReconcileBase(models.AbstractModel):
    _inherit = "mass.reconcile.base"

    # WARNING: this has limitation as it creates a job based on an object wizard
    # when the transient model will be garbadge collected the job won't
    # be able to run anymore.
    # FIXME: move or copy wizard data configuration in a standard model or refactor
    # to have it as a parameter.

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
            self.with_delay().reconcile_lines_as_job(
                lines,
                allow_partial=allow_partial
            )
            # Report is not available with reconcile jobs
            return False, False
        else:
            return super()._reconcile_lines(lines, allow_partial=allow_partial)

    def reconcile_lines_as_job(self, lines, allow_partial=False):
        self.with_context(reconcile_lines_as_job=False)._reconcile_lines(lines, allow_partial=allow_partial)
