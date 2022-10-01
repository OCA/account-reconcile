# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models


class AccountMassReconcileMethod(models.Model):
    _inherit = "account.mass.reconcile.method"

    def _selection_name(self):
        methods = super(AccountMassReconcileMethod, self)._selection_name()
        methods += [
            (
                "mass.reconcile.advanced.by.mrp.production",
                "Advanced. Mrp production.",
            ),
            (
                "mass.reconcile.advanced.by.unbuild",
                "Advanced. Unbuild Order.",
            ),
        ]
        return methods
