# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountReconcileManualModel(models.Model):
    _name = "account.reconcile.manual.model"
    _description = "Models for Manual Reconcile Write-off"
    _check_company_auto = True
    _rec_name = "ref"
    _order = "sequence, id"

    sequence = fields.Integer()
    company_id = fields.Many2one(
        "res.company", ondelete="cascade", required=True, index=True
    )
    ref = fields.Char(string="Write-off Reference", required=True)
    expense_account_id = fields.Many2one(
        "account.account",
        string="Expense Write-off Account",
        required=True,
        domain="[('company_id', '=', company_id), ('deprecated', '=', False), "
        "('internal_group', '=', 'expense')]",
        check_company=True,
    )
    income_account_id = fields.Many2one(
        "account.account",
        string="Income Write-off Account",
        required=True,
        domain="[('company_id', '=', company_id), ('deprecated', '=', False), "
        "('internal_group', '=', 'income')]",
        check_company=True,
    )
    expense_analytic_distribution = fields.Json(
        string="Analytic for Expense",
        compute="_compute_analytic_distribution",
        store=True,
        readonly=False,
        precompute=True,
    )
    income_analytic_distribution = fields.Json(
        string="Analytic for Income",
        compute="_compute_analytic_distribution",
        store=True,
        readonly=False,
        precompute=True,
    )
    analytic_precision = fields.Integer(
        default=lambda self: self.env["decimal.precision"].precision_get(
            "Percentage Analytic"
        ),
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Write-off Journal",
        required=True,
        domain="[('type', '=', 'general'), ('company_id', '=', company_id)]",
        check_company=True,
    )

    _sql_constraints = [
        (
            "ref_company_uniq",
            "unique(ref, company_id)",
            "This write-off model already exists in this company!",
        )
    ]

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res["company_id"] = self.env.company.id
        journals = self.env["account.journal"].search(
            [("company_id", "=", res["company_id"]), ("type", "=", "general")]
        )
        if len(journals) == 1:
            res["journal_id"] = journals.id
        return res

    @api.depends("expense_account_id", "income_account_id")
    def _compute_analytic_distribution(self):
        aadmo = self.env["account.analytic.distribution.model"]
        for model in self:
            expense_distri = aadmo._get_distribution(
                {
                    "account_prefix": model.expense_account_id.code,
                    "company_id": model.company_id.id,
                }
            )
            income_distri = aadmo._get_distribution(
                {
                    "account_prefix": model.income_account_id.code,
                    "company_id": model.company_id.id,
                }
            )
            model.expense_analytic_distribution = expense_distri
            model.income_analytic_distribution = income_distri
