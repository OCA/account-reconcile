# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import api, fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    add_sale_order_id = fields.Many2one(
        "sale.order",
        check_company=True,
        store=False,
        default=False,
        prefetch=False,
    )

    @api.onchange("add_sale_order_id")
    def _onchange_add_sale_order_id(self):
        new_data = []
        to_add = True

        for line in self.reconcile_data_info["data"]:
            if line.get("sale_order_id") == self.add_sale_order_id.id:
                to_add = False
                continue
            new_data.append(line)

        if to_add:
            new_data.append(
                self._get_reconcile_line_for_sale_order(
                    self.add_sale_order_id,
                    "other",
                    self.reconcile_data_info["reconcile_auxiliary_id"],
                )
            )
            self.reconcile_data_info["reconcile_auxiliary_id"] += 1

        self.reconcile_data_info = self._recompute_suspense_line(
            new_data,
            self.reconcile_data_info["reconcile_auxiliary_id"],
            self.manual_reference,
        )
        self.can_reconcile = self.reconcile_data_info.get("can_reconcile", False)

    def _default_reconcile_data(self, from_unreconcile=False):
        self = self.with_context(account_reconcile_sale_order_inject_rule_type=True)
        return super()._default_reconcile_data(from_unreconcile=from_unreconcile)

    def _get_reconcile_line(
        self,
        line,
        kind,
        is_counterpart=False,
        max_amount=False,
        from_unreconcile=False,
        reconcile_auxiliary_id=False,
        move=False,
        is_reconciled=False,
    ):
        if isinstance(line, models.Model) and line._name == "sale.order":
            return reconcile_auxiliary_id + len(line), [
                self._get_reconcile_line_for_sale_order(
                    sale_order, kind, reconcile_auxiliary_id + i
                )
                for i, sale_order in enumerate(line)
            ]

        return super()._get_reconcile_line(
            line,
            kind,
            is_counterpart=is_counterpart,
            max_amount=max_amount,
            from_unreconcile=from_unreconcile,
            reconcile_auxiliary_id=reconcile_auxiliary_id,
            move=move,
            is_reconciled=is_reconciled,
        )

    def _get_reconcile_line_for_sale_order(
        self, sale_order, kind, reconcile_auxiliary_id
    ):
        """
        Return dict to be added to reconcile_data_info["data"] for sales order
        """
        account = sale_order.partner_id.property_account_receivable_id
        return {
            "id": False,
            "reference": f"reconcile_auxiliary;{reconcile_auxiliary_id}",
            "account_id": (account.id, self.env._("Sales Order %s", sale_order.name)),
            "partner_id": (
                sale_order.partner_id.id,
                sale_order.partner_id.display_name,
            ),
            "date": fields.Date.to_string(sale_order.date_order),
            "name": sale_order.name,
            "amount": -sale_order.amount_total,
            "credit": sale_order.amount_total,
            "debit": 0,
            "kind": kind,
            "currency_id": sale_order.currency_id.id,
            "currency_amount": -sale_order.amount_total,
            "line_currency_id": sale_order.currency_id.id,
            "sale_order_id": sale_order.id,
        }

    def _prepare_reconcile_line_data(self, lines):
        for line in lines:
            if line.get("sale_order_id"):
                sale_order = self.env["sale.order"].browse(line["sale_order_id"])
                counterpart_lines = (
                    self._prepare_reconcile_line_data_sale_order_invoice(sale_order)
                )
                line["counterpart_line_ids"] = counterpart_lines.ids

        return super()._prepare_reconcile_line_data(lines)

    def _prepare_reconcile_line_data_sale_order_invoice(self, order):
        """
        Invoice selected sales orders and post the invoices
        """
        if order.state in ("draft", "sent"):
            order.action_confirm()
        invoices = order._create_invoices()
        invoices.action_post()
        return invoices.line_ids.filtered(
            lambda x: x.account_id.account_type == "asset_receivable"
        )
