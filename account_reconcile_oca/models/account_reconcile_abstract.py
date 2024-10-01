# Copyright 2023 Dixmit
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
    currency_id = fields.Many2one("res.currency", readonly=True)
    foreign_currency_id = fields.Many2one("res.currency")
    company_currency_id = fields.Many2one(
        related="company_id.currency_id", string="Company Currency"
    )

    def _get_reconcile_currency(self):
        return self.currency_id or self.company_id._currency_id

    def _get_reconcile_line(
        self,
        line,
        kind,
        is_counterpart=False,
        max_amount=False,
        from_unreconcile=False,
        move=False,
    ):
        date = self.date if "date" in self._fields else line.date
        original_amount = amount = net_amount = line.debit - line.credit
        line_currency = line.currency_id
        if is_counterpart:
            currency_amount = -line.amount_residual_currency or line.amount_residual
            amount = -line.amount_residual
            currency = line.currency_id or line.company_id.currency_id
            original_amount = net_amount = -line.amount_residual
            if max_amount:
                dest_currency = self._get_reconcile_currency()
                if currency == dest_currency:
                    real_currency_amount = currency_amount
                elif self.company_id.currency_id == dest_currency:
                    real_currency_amount = amount
                else:
                    real_currency_amount = self.company_id.currency_id._convert(
                        amount,
                        dest_currency,
                        self.company_id,
                        date,
                    )
                if (
                    -real_currency_amount > max_amount > 0
                    or -real_currency_amount < max_amount < 0
                ):
                    currency_max_amount = self._get_reconcile_currency()._convert(
                        max_amount, currency, self.company_id, date
                    )
                    amount = currency_max_amount
                    net_amount = -max_amount
                    currency_amount = -amount
                    amount = currency._convert(
                        currency_amount,
                        self.company_id.currency_id,
                        self.company_id,
                        date,
                    )
        else:
            currency_amount = self.amount_currency or self.amount
            line_currency = self._get_reconcile_currency()
        vals = {
            "move_id": move and line.move_id.id,
            "move": move and line.move_id.name,
            "reference": "account.move.line;%s" % line.id,
            "id": line.id,
            "account_id": line.account_id.name_get()[0],
            "partner_id": line.partner_id and line.partner_id.name_get()[0] or False,
            "date": fields.Date.to_string(line.date),
            "name": line.name,
            "debit": amount if amount > 0 else 0.0,
            "credit": -amount if amount < 0 else 0.0,
            "amount": amount,
            "net_amount": amount - net_amount,
            "currency_id": self.company_id.currency_id.id,
            "line_currency_id": line_currency.id,
            "currency_amount": currency_amount,
            "analytic_distribution": line.analytic_distribution,
            "kind": kind,
        }
        if from_unreconcile:
            vals.update(
                {
                    "credit": vals["debit"] and from_unreconcile["debit"],
                    "debit": vals["credit"] and from_unreconcile["credit"],
                    "amount": from_unreconcile["amount"],
                    "net_amount": from_unreconcile["amount"],
                    "currency_amount": from_unreconcile["currency_amount"],
                }
            )
        if not float_is_zero(
            amount - original_amount, precision_digits=line.currency_id.decimal_places
        ):
            vals["original_amount"] = abs(original_amount)
            vals["original_amount_unsigned"] = original_amount
        if is_counterpart:
            vals["counterpart_line_ids"] = line.ids
        return [vals]
