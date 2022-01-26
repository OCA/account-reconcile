# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class MassReconcileAdvancedBySaleLine(models.TransientModel):
    _name = "mass.reconcile.advanced.by.sale.line"
    _inherit = "mass.reconcile.advanced"
    _description = "Mass Reconcile By Sale Line"

    @staticmethod
    def _skip_line(move_line):
        """
        When True is returned on some conditions, the credit move line
        will be skipped for reconciliation. Can be inherited to
        skip on some conditions. ie: ref or partner_id is empty.
        """
        return not (move_line.get("product_id") and move_line.get("sale_line_id"))

    @staticmethod
    def _matchers(move_line):
        return (("sale_line_id", move_line["sale_line_id"]),)

    @staticmethod
    def _opposite_matchers(move_line):
        yield ("sale_line_id", move_line["sale_line_id"])
