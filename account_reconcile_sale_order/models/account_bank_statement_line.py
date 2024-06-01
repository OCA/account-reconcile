# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def process_reconciliation(
        self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None
    ):
        """
        Invoice selected sale orders and use resulting move lines
        """
        new_aml_dicts2 = []
        counterpart_aml_dicts = (counterpart_aml_dicts or [])[:]
        for new_aml_dict in new_aml_dicts or []:
            sale_order_id = new_aml_dict.get("sale_order_id")
            if sale_order_id:
                order = self.env["sale.order"].browse(sale_order_id)
                self._process_reconciliation_sale_order_invoice(order)
                counterpart_aml_dicts += (
                    self._process_reconciliation_sale_order_counterparts(order)
                )
            else:
                new_aml_dicts2.append(new_aml_dict)

        return super().process_reconciliation(
            counterpart_aml_dicts=counterpart_aml_dicts,
            payment_aml_rec=payment_aml_rec,
            new_aml_dicts=new_aml_dicts2,
        )

    def _process_reconciliation_sale_order_invoice(self, order):
        """
        Invoice selected sale orders and post the invoices
        """
        clean_context = {
            key: value
            for key, value in self.env.context.items()
            if key != "force_price_include"
        }
        order = order.with_context(clean_context)  # pylint: disable=context-overridden
        if order.state in ("draft", "sent"):
            order.action_confirm()
        invoices = order._create_invoices()
        invoices.action_post()

    def _process_reconciliation_sale_order_counterparts(self, order):
        """
        Return counterpart aml dicts for sale order
        """
        return [
            {
                "name": line.name,
                "move_line": line,
                "debit": line.credit,
                "credit": line.debit,
                "analytic_tag_ids": [(6, 0, line.analytic_tag_ids.ids)],
            }
            for line in order.mapped("invoice_ids.line_ids")
            if line.account_id.user_type_id.type == "receivable"
        ]
