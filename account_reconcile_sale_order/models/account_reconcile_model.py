# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import api, fields, models
from odoo.osv.expression import is_leaf


class AccountReconcileModel(models.AbstractModel):
    _inherit = "account.reconcile.model"

    rule_type = fields.Selection(
        selection_add=[("sale_order_matching", "Rule to match sales orders")],
        ondelete={"sale_order_matching": "cascade"},
    )
    sale_order_matching_token_match = fields.Boolean(
        string="Match tokens",
        help="When this is activated, the statement line's label is split into words "
        "and if one of those words match a sales order, it is considered a match. So "
        "if the statement line's label is 'hello world', sales orders with names "
        "'hello', 'world', 'some name containing hello', 'some name containing world' "
        "will be considered matches, in that order",
    )
    sale_order_matching_token_length = fields.Integer(
        string="Minimum token length",
        default=3,
        help="Set the minimum word length to search for. If you set this to 4, and the "
        "statement line's label is 'hello you', it will only search for 'hello', not "
        "for 'you'",
    )
    sale_order_matching_payment_method_ids = fields.Many2many(
        comodel_name="payment.method",
        relation="account_reconcile_model_sale_order_payment_method_rel",
        string="Payment methods",
        help="Set this field to restrict sales order matching to specific payment "
        "methods used on the SO's payment transaction",
    )

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        if self.env.context.get("account_reconcile_sale_order_inject_rule_type"):
            domain = [
                leaf
                if not is_leaf(leaf) or leaf[0] != "rule_type" or leaf[1] != "in"
                else tuple(list(leaf[:2]) + [list(leaf[2] + ["sale_order_matching"])])
                for leaf in domain
            ]
        return super()._search(domain, offset=offset, limit=limit, order=order)

    def _apply_rules(self, st_line, partner):
        for this in self.sorted():
            result = super(AccountReconcileModel, this)._apply_rules(st_line, partner)
            if result:
                return result
            if this.rule_type == "sale_order_matching":
                if not this._is_applicable_for(st_line, partner):
                    continue
                sale_orders = self.env["sale.order"]
                while found_order := this._get_candidates_sale_order_best_match(
                    st_line, partner, sale_orders.ids or None
                ):
                    sale_orders += found_order
                if sale_orders:
                    return {
                        "status": "sale_order_matching",
                        "model": this,
                        "amls": sale_orders,
                        "auto_reconcile": this.auto_reconcile,
                    }
        return {}

    def _get_sale_orders_for_bank_statement_line_domain(
        self,
        bank_statement_line,
        partner=None,
        excluded_ids=None,
        amount=None,
        extra_domain=None,
    ):
        return (
            [
                ("state", "not in", ("done", "cancel")),
                ("partner_id", "=?", partner.id),
                ("amount_total", "=?", amount),
                ("invoice_status", "not in", ("upselling", "invoiced")),
            ]
            + ([("id", "not in", excluded_ids)] if excluded_ids else [])
            + (
                self.sale_order_matching_payment_method_ids
                and [
                    (
                        "transaction_ids.payment_method_id",
                        "in",
                        self.sale_order_matching_payment_method_ids.ids,
                    )
                ]
                or []
            )
            + (extra_domain or [])
        )

    def _get_candidates_sale_order_best_match(
        self, bank_statement_line, partner, excluded_ids
    ):
        """
        Return one sales order that is considered the best match for some line and
        partner
        """

        def domain(extra_domain):
            return self._get_sale_orders_for_bank_statement_line_domain(
                bank_statement_line,
                partner,
                excluded_ids=excluded_ids,
                extra_domain=extra_domain,
            )

        def search(domain):
            return self.env["sale.order"].search(domain, limit=1)

        def first(field, operator, tokens):
            return sum(
                (search(domain([(field, operator, token)])) for token in tokens),
                self.env["sale.order"],
            )[:1]

        ref = bank_statement_line.payment_ref or ""
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
