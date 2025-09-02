# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import Command, api, fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    manual_analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        string="Analytic Tags",
        check_company=True,
    )

    def _get_manual_delete_vals(self):
        vals = super()._get_manual_delete_vals()
        vals["manual_analytic_tag_ids"] = False
        return vals

    def _process_manual_reconcile_from_line(self, line):
        res = super()._process_manual_reconcile_from_line(line)
        self.manual_analytic_tag_ids = line.get("manual_analytic_tag_ids")
        return res

    def _get_manual_reconcile_vals(self):
        vals = super()._get_manual_reconcile_vals()
        vals["manual_analytic_tag_ids"] = [
            Command.set(self.manual_analytic_tag_ids.ids)
        ]
        return vals

    @api.onchange("manual_analytic_tag_ids")
    def _onchange_analytic_tag_ids(self):
        return super()._onchange_manual_reconcile_vals()

    def _reconcile_move_line_vals(self, line, move_id=False):
        vals = super()._reconcile_move_line_vals(line=line, move_id=move_id)
        vals["analytic_tag_ids"] = line.get("manual_analytic_tag_ids")
        return vals
