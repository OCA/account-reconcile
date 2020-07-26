# Copyright 2015-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import models


class AccountMassReconcileMethod(models.Model):

    _inherit = "account.mass.reconcile.method"

    def _selection_name(self):
        methods = super()._selection_name()
        methods += [
            (
                "mass.reconcile.advanced.ref.deep.search",
                "Advanced. Partner and Ref. Deep Search",
            ),
        ]
        return methods
