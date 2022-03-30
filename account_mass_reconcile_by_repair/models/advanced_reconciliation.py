# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class MassReconcileAdvancedByRepairOrder(models.TransientModel):
    _name = "mass.reconcile.advanced.by.repair.order"
    _inherit = "mass.reconcile.advanced"
    _description = "Mass Reconcile By Repair Order"

    @staticmethod
    def _skip_line(move_line):
        """
        When True is returned on some conditions, the credit move line
        will be skipped for reconciliation. Can be inherited to
        skip on some conditions. ie: ref or partner_id is empty.
        """
        return not (move_line.get("repair_order_id"))

    @staticmethod
    def _matchers(move_line):
        return (("repair_order_id", move_line["repair_order_id"]),)

    @staticmethod
    def _opposite_matchers(move_line):
        yield ("repair_order_id", move_line["repair_order_id"])
