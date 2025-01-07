# Copyright 2024-2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class AccountReconcileModelLine(models.Model):
    _inherit = "account.reconcile.model.line"

    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        string="Analytic Tags",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    def _get_write_off_move_line_dict(self, balance, currency):
        vals = super()._get_write_off_move_line_dict(balance, currency)
        vals["manual_analytic_tag_ids"] = [(6, 0, self.analytic_tag_ids.ids)]
        return vals
