# © 2015-18 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class MassReconcileAdvanced(models.AbstractModel):
    _inherit = 'mass.reconcile.advanced'

    def _selection_columns(self):
        aml_cols = super(MassReconcileAdvanced, self)._selection_columns()
        aml_cols.append('account_move_line.purchase_line_id')
        aml_cols.append('account_move_line.product_id')
        return aml_cols
