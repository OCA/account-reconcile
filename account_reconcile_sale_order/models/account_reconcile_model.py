# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class AccountReconcileModel(models.AbstractModel):
    _inherit = "account.reconcile.model"

    rule_type = fields.Selection(
        selection_add=[("sale_order_matching", "Rule to match sale orders")],
        ondelete={"sale_order_matching": "cascade"},
    )
    sale_order_matching_token_match = fields.Boolean(
        string="Match tokens",
        help="When this is activated, the statement line's label is split into words "
        "and if one of those words match a sale order, it is considered a match. So "
        "if the statement line's label is 'hello world', sale orders with names 'hello', "
        "'world', 'some name containing hello', 'some name containing world' will be "
        "considered matches, in that order",
    )
    sale_order_matching_token_length = fields.Integer(
        string="Minimum token length",
        default=3,
        help="Set the minimum word length to search for. If you set this to 4, and the "
        "statement line's label is 'hello you', it will only search for 'hello', not "
        "for 'you'",
    )

    def _get_candidates(self, st_lines_with_partner, excluded_ids):
        if self.rule_type == "sale_order_matching":
            return self._get_candidates_sale_order(st_lines_with_partner, excluded_ids)
        else:
            return super()._get_candidates(st_lines_with_partner, excluded_ids)

    def _get_rule_result(
        self, st_line, candidates, aml_ids_to_exclude, reconciled_amls_ids, partner_map
    ):
        if self.rule_type == "sale_order_matching":
            return self._get_rule_result_sale_order(
                st_line,
                candidates,
                aml_ids_to_exclude,
                reconciled_amls_ids,
                partner_map,
            )
        else:
            return super()._get_rule_result(
                st_line,
                candidates,
                aml_ids_to_exclude,
                reconciled_amls_ids,
                partner_map,
            )

    def _get_candidates_sale_order(self, st_lines_with_partner, excluded_ids):
        """Return candidates for matching sale orders"""
        return {
            line.id: self._get_candidates_sale_order_best_match(
                line, partner, excluded_ids
            )
            for line, partner in st_lines_with_partner
        }

    def _get_candidates_sale_order_best_match(
        self, bank_statement_line, partner, excluded_ids
    ):
        """Return one sale order that is considered the best match for some line and partner"""

        def domain(extra_domain):
            widget = self.env["account.reconciliation.widget"]
            return widget._get_sale_orders_for_bank_statement_line_domain(
                bank_statement_line.id,
                partner.id,
                amount=bank_statement_line.amount,
                excluded_ids=excluded_ids,
                extra_domain=extra_domain,
            )

        def search(domain):
            return self.env["sale.order"].search(domain, limit=1)

        def first(field, operator, tokens):
            return sum(
                (search([(field, operator, token)]) for token in tokens),
                self.env["sale.order"],
            )[:1]

        ref = bank_statement_line.payment_ref
        tokens = list(
            filter(
                lambda x: len(x) >= self.sale_order_matching_token_length, ref.split()
            )
        )

        return (
            search(domain([("name", "=ilike", ref)]))
            or search(domain([("partner_id", "=ilike", ref)]))
            or (
                (first("name", "=ilike", tokens) or first("name", "ilike", tokens))
                if self.sale_order_matching_token_match
                else self.env["sale.order"]
            )
        )

    def _get_rule_result_sale_order(
        self, st_line, candidates, aml_ids_to_exclude, reconciled_amls_ids, partner_map
    ):
        return (
            {
                "model": self,
                "status": "sale_order_matching",
                "aml_ids": candidates,
                "write_off_vals": [
                    self.env[
                        "account.reconciliation.widget"
                    ]._reconciliation_proposition_from_sale_order(order)
                    for order in candidates
                ],
            },
            set(),
            set(),
        )
