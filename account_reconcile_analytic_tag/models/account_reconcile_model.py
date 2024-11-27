# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"

    # TODO: Remove if merging https://github.com/odoo/odoo/pull/188808
    def _get_write_off_move_lines_dict(self, residual_balance, partner_id):
        res = super()._get_write_off_move_lines_dict(
            residual_balance=residual_balance, partner_id=partner_id
        )
        if len(res) == 0:
            return res
        currency = self.company_id.currency_id
        for index, line in enumerate(self.line_ids):
            if line.amount_type == "percentage":
                balance = currency.round(residual_balance * (line.amount / 100.0))
            elif line.amount_type == "fixed":
                balance = currency.round(
                    line.amount * (1 if residual_balance > 0.0 else -1)
                )
            else:
                balance = 0.0

            if currency.is_zero(balance):
                continue

            res[index]["manual_analytic_tag_ids"] = [(6, 0, line.analytic_tag_ids.ids)]
        return res


class AccountReconcileModelLine(models.Model):
    _inherit = "account.reconcile.model.line"

    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        string="Analytic Tags",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    # TODO: Use if merging https://github.com/odoo/odoo/pull/188808
    # def _get_write_off_move_line_dict(self, balance):
    #     vals = super()._get_write_off_move_line_dict(balance)
    #     vals["manual_analytic_tag_ids"] = [(6, 0, self.analytic_tag_ids.ids)]
    #     return vals
