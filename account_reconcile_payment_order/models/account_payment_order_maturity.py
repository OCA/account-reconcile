# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountPaymentOrderMaturity(models.Model):

    _name = "account.payment.order.maturity"
    _description = "Account Payment Order Maturity"  # TODO

    payment_order_id = fields.Many2one(
        "account.payment.order", required=True, ondelete="cascade"
    )
    currency_id = fields.Many2one("res.currency", required=True)
    date = fields.Date(required=True)
    company_id = fields.Many2one(
        "res.company", related="payment_order_id.company_id", store=True
    )
    payment_ids = fields.One2many("account.payment", inverse_name="maturity_order_id")
    payment_type = fields.Selection(related="payment_order_id.payment_type", store=True)
    is_matched = fields.Boolean(compute="_compute_matched_info", store=True)
    amount_residual = fields.Monetary(
        compute="_compute_matched_info", store=True, currency_field="currency_id"
    )

    @api.depends(
        "payment_ids",
        "payment_ids.is_matched",
        "payment_ids.move_id.line_ids.amount_residual",
    )
    def _compute_matched_info(self):
        for record in self:
            record.is_matched = all(record.mapped("payment_ids.is_matched"))
            residual_field = (
                "amount_residual"
                if record.currency_id == record.company_id.currency_id
                else "amount_residual_currency"
            )
            amount_residual = 0.0
            for pay in record.mapped("payment_ids"):
                (
                    liquidity_lines,
                    counterpart_lines,
                    writeoff_lines,
                ) = pay._seek_for_lines()
                amount_residual += sum(liquidity_lines.mapped(residual_field))
            record.amount_residual = amount_residual

    def action_view_order(self):
        self.ensure_one()
        return self.payment_order_id.get_formview_action()
