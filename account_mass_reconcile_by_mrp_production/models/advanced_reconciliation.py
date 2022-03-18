# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class MassReconcileAdvancedByMrpProduction(models.TransientModel):
    _name = "mass.reconcile.advanced.by.mrp.production"
    _inherit = "mass.reconcile.advanced"
    _description = "Mass Reconcile By Mrp Production"

    @staticmethod
    def _skip_line(move_line):
        """
        When True is returned on some conditions, the credit move line
        will be skipped for reconciliation. Can be inherited to
        skip on some conditions. ie: ref or partner_id is empty.
        """
        return not (move_line.get("mrp_production_id"))

    @staticmethod
    def _matchers(move_line):
        return (("mrp_production_id", move_line["mrp_production_id"]),)

    @staticmethod
    def _opposite_matchers(move_line):
        yield ("mrp_production_id", move_line["mrp_production_id"])


class MassReconcileAdvancedByUnbuild(models.TransientModel):
    _name = "mass.reconcile.advanced.by.unbuild"
    _inherit = "mass.reconcile.advanced"
    _description = "Mass Reconcile By Unbuild Order"

    @staticmethod
    def _skip_line(move_line):
        """
        When True is returned on some conditions, the credit move line
        will be skipped for reconciliation. Can be inherited to
        skip on some conditions. ie: ref or partner_id is empty.
        """
        return not (move_line.get("unbuild_id"))

    @staticmethod
    def _matchers(move_line):
        return (("unbuild_id", move_line["unbuild_id"]),)

    @staticmethod
    def _opposite_matchers(move_line):
        yield ("unbuild_id", move_line["unbuild_id"])
