# Copyright (C) 2021, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import api, fields, models


class AccountFullReconcile(models.Model):
    _inherit = "account.full.reconcile"
    _description = "Full Reconcile"

    reconciliation_date = fields.Date(
        string="Reconciliation Date", default=date.today()
    )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        for reconcile_id in res:
            for line_id in reconcile_id.reconciled_line_ids:
                if line_id.payment_id:
                    line_id.payment_id.reconciliation_date = (
                        reconcile_id.reconciliation_date
                    )
                if line_id.move_id:
                    line_id.move_id.reconciliation_date = (
                        reconcile_id.reconciliation_date
                    )
        return res
