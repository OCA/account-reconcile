# © 2015-18 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class MassReconcileAdvanced(models.AbstractModel):
    _inherit = 'mass.reconcile.advanced'

    @staticmethod
    def _base_columns():
        """ Mandatory columns for move lines queries
        An extra column aliased as ``key`` should be defined
        in each query."""
        aml_cols = super(MassReconcileAdvanced, MassReconcileAdvanced).\
            _base_columns()
        aml_cols.append('account_move_line.purchase_line_id')
        aml_cols.append('account_move_line.product_id')
        return aml_cols
