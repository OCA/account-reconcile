# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import api, models
from odoo.tools.misc import format_date, formatLang


class AccountReconciliationWidget(models.AbstractModel):
    _inherit = "account.reconciliation.widget"

    @api.model
    def _prepare_move_lines(
        self, move_lines, target_currency=False, target_date=False, recs_count=0
    ):
        if (
            move_lines.ids
            and isinstance(move_lines.ids[0], models.Model)
            and move_lines.ids[0]._name == "sale.order"
        ):
            return [
                self._reconciliation_proposition_from_sale_order(order)
                for order in move_lines.ids
            ]
        return super()._prepare_move_lines(
            move_lines,
            target_currency=target_currency,
            target_date=target_date,
            recs_count=recs_count,
        )

    @api.model
    def get_move_lines_for_bank_statement_line(
        self,
        st_line_id,
        partner_id=None,
        excluded_ids=None,
        search_str=False,
        offset=0,
        limit=None,
        mode=None,
    ):
        """
        Prepend matching sale orders to move line propositions
        """
        result = super().get_move_lines_for_bank_statement_line(
            st_line_id,
            partner_id=partner_id,
            excluded_ids=excluded_ids,
            search_str=search_str,
            offset=offset,
            limit=limit,
            mode=mode,
        )
        sale_orders = []
        if mode == "rp":
            sale_orders = self._get_sale_orders_for_bank_statement_line(
                st_line_id,
                partner_id=partner_id,
                excluded_ids=excluded_ids,
                search_str=search_str,
                offset=offset,
                limit=limit,
            )
        return sale_orders + result

    @api.model
    def _get_sale_orders_for_bank_statement_line(
        self,
        st_line_id,
        partner_id=None,
        excluded_ids=None,
        search_str=False,
        offset=0,
        limit=None,
    ):
        result = []
        for order in self.env["sale.order"].search(
            self._get_sale_orders_for_bank_statement_line_domain(
                st_line_id,
                partner_id=partner_id,
                excluded_ids=excluded_ids,
                extra_domain=[
                    "|",
                    ("name", "ilike", search_str),
                    ("partner_id", "ilike", search_str),
                ]
                if search_str
                else None,
            ),
            limit=limit,
        ):
            result.append(self._reconciliation_proposition_from_sale_order(order))
        return result

    @api.model
    def _get_sale_orders_for_bank_statement_line_domain(
        self,
        st_line_id,
        partner_id=None,
        excluded_ids=None,
        amount=None,
        extra_domain=None,
    ):
        return (
            [
                ("state", "not in", ("done", "cancel")),
                ("partner_id", "=?", partner_id),
                ("amount_total", "=?", amount),
                ("invoice_status", "not in", ("upselling", "invoiced")),
            ]
            + ([("id", "not in", excluded_ids)] if excluded_ids else [])
            + (extra_domain or [])
        )

    @api.model
    def _reconciliation_proposition_from_sale_order(self, order):
        journal = (
            self.env["account.move"]
            .with_context(default_move_type="out_invoice")
            ._get_default_journal()
        )
        account = order.partner_id.property_account_receivable_id
        return {
            "id": "so_%d" % order.id,
            "name": order.name,
            "ref": order.reference or order.client_order_ref or order.origin or "",
            "already_paid": False,
            "account_type": "receivable",
            "date_maturity": format_date(self.env, order.date_order),
            "date": format_date(self.env, order.date_order),
            "partner_id": order.partner_id.id,
            "partner_name": order.partner_id.name,
            "currency_id": order.currency_id.id,
            "debit": order.amount_total,
            "credit": 0,
            "amount_str": formatLang(
                self.env,
                order.amount_total,
                currency_obj=order.currency_id,
            ),
            "total_amount_str": formatLang(
                self.env,
                order.amount_total,
                currency_obj=order.currency_id,
            ),
            "sale_order_id": order.id,
            "recs_count": 1,
            "amount_currency": "",
            "amount_currency_str": "",
            "total_amount_currency_str": "",
            "account_id": [account.id, account.name],
            "account_code": account.code,
            "account_name": account.name,
            "journal_id": [journal.id, journal.name],
        }
