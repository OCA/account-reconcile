# Copyright 2022 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import float_is_zero


class AccountReconcileAbstract(models.AbstractModel):
    _name = "account.reconcile.abstract"
    _description = "Account Reconcile Abstract"

    reconcile_data_info = fields.Serialized(
        compute="_compute_reconcile_data_info",
        prefetch=False,
    )
    company_id = fields.Many2one("res.company")
    add_account_move_line_id = fields.Many2one(
        "account.move.line",
        check_company=True,
        store=False,
        default=False,
        prefetch=False,
    )
    manual_reference = fields.Char(store=False, default=False, prefetch=False)
    manual_delete = fields.Boolean(
        store=False,
        default=False,
        prefetch=False,
    )

    def _get_reconcile_line(self, line, kind, is_counterpart=False, max_amount=False):
        original_amount = amount = line.debit - line.credit
        if is_counterpart:
            original_amount = amount = (
                line.amount_residual_currency or line.amount_residual
            )
        if max_amount:
            if amount > max_amount > 0:
                amount = max_amount
            if amount < max_amount < 0:
                amount = max_amount
        if is_counterpart:
            amount = -amount
            original_amount = -original_amount
        vals = {
            "reference": "account.move.line;%s" % line.id,
            "id": line.id,
            "account_id": line.account_id.name_get()[0],
            "partner_id": line.partner_id and line.partner_id.name_get()[0] or False,
            "date": fields.Date.to_string(line.date),
            "name": line.name,
            "debit": amount if amount > 0 else 0.0,
            "credit": -amount if amount < 0 else 0.0,
            "amount": amount,
            "currency_id": line.currency_id.id,
            "analytic_distribution": line.analytic_distribution,
            "kind": kind,
        }
        if not float_is_zero(
            amount - original_amount, precision_digits=line.currency_id.decimal_places
        ):
            vals["original_amount"] = abs(original_amount)
            vals["original_amount_unsigned"] = original_amount
        if is_counterpart:
            vals["counterpart_line_id"] = line.id
        return vals
