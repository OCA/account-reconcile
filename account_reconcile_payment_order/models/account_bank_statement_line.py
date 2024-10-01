# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountBankStatementLine(models.Model):

    _inherit = "account.bank.statement.line"

    payment_type_filter = fields.Selection(
        selection=lambda r: r.env["account.payment.order"]
        ._fields["payment_type"]
        .selection,
        compute="_compute_payment_type_filter",
    )
    add_payment_order_id = fields.Many2one(
        "account.payment.order.maturity",
        check_company=True,
        store=False,
        default=False,
        prefetch=False,
    )

    @api.depends()
    def _compute_payment_type_filter(self):
        for record in self:
            record.payment_type_filter = "inbound" if record.amount > 0 else "outbound"

    def clean_reconcile(self):
        """
        Remove the counterparts when cleaning
        """
        res = super().clean_reconcile()
        data = self.reconcile_data_info
        data["order_counterparts"] = []
        self.reconcile_data_info = data
        return res

    @api.onchange("add_payment_order_id")
    def _onchange_add_payment_order_id(self):
        """
        We need to check if the payment order is in already on the counterpart.
        In this case we need to add all the liquidity lines. Otherwise, we remove them
        """
        if self.add_payment_order_id:
            data = self.reconcile_data_info["data"]
            if self.add_payment_order_id.id not in self.reconcile_data_info.get(
                "order_counterparts", []
            ):
                new_data = []
                counterparts = []
                for line in data:
                    counterparts += line.get("counterpart_line_ids", [])
                    new_data.append(line)
                for payment in self.add_payment_order_id.payment_ids.filtered(
                    lambda r: not r.is_matched
                ):
                    (
                        liquidity_lines,
                        counterpart_lines,
                        writeoff_lines,
                    ) = payment._seek_for_lines()
                    for line in liquidity_lines.filtered(
                        lambda r: r.id not in counterparts
                    ):
                        reconcile_auxiliary_id, lines = self._get_reconcile_line(
                            line, "other", True, 0.0
                        )
                        new_data += lines
                data_info = self._recompute_suspense_line(
                    new_data,
                    self.reconcile_data_info["reconcile_auxiliary_id"],
                    self.manual_reference,
                )
                data_info["order_counterparts"].append(self.add_payment_order_id.id)
                self.reconcile_data_info = data_info
            elif self.add_payment_order_id:
                data = self.reconcile_data_info["data"]
                lines = []
                for payment in self.add_payment_order_id.payment_ids.filtered(
                    lambda r: not r.is_matched
                ):
                    (
                        liquidity_lines,
                        counterpart_lines,
                        writeoff_lines,
                    ) = payment._seek_for_lines()
                    lines += liquidity_lines.ids
                new_data = []
                for line in data:
                    if set(line.get("counterpart_line_ids", [])).intersection(
                        set(lines)
                    ):
                        continue
                    new_data.append(line)
                data_info = self._recompute_suspense_line(
                    new_data,
                    self.reconcile_data_info["reconcile_auxiliary_id"],
                    self.manual_reference,
                )
                ["order_counterparts"].append(self.add_payment_order_id.id)
                counterparts = set(data_info["order_counterparts"])
                counterparts.remove(self.add_payment_order_id.id)
                data_info["order_counterparts"] = list(counterparts)
                self.reconcile_data_info = data_info
            self.add_payment_order_id = False

    def _recompute_suspense_line(self, data, reconcile_auxiliary_id, manual_reference):
        """
        We want to keep the counterpart when we recompute
        """
        order_counterparts = (
            self.reconcile_data_info
            and self.reconcile_data_info.get("order_counterparts", [])
        ) or []
        result = super()._recompute_suspense_line(
            data, reconcile_auxiliary_id, manual_reference
        )
        result["order_counterparts"] = order_counterparts
        return result
