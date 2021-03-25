# -*- coding: utf-8 -*-
# # Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models


class MassReconcileAdvanced(models.AbstractModel):
    _inherit = 'mass.reconcile.advanced'

    def _base_columns(self):
        aml_cols = super(MassReconcileAdvanced, self)._base_columns()
        aml_cols.append('account_move_line.sale_line_id')
        aml_cols.append('account_move_line.product_id')
        return aml_cols
