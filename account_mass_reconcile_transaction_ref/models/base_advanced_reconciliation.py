# Copyright 2013-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import models


class MassReconcileAdvanced(models.AbstractModel):

    _inherit = 'mass.reconcile.advanced'

    def _base_columns(self):
        """ Mandatory columns for move lines queries
        An extra column aliased as ``key`` should be defined
        in each query."""
        aml_cols = super(MassReconcileAdvanced, self)._base_columns()
        aml_cols.append('account_move_line.transaction_ref')
        return aml_cols
