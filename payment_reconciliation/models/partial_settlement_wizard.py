import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PartialSettlementWizard(models.TransientModel):
    _name = "partial.settlement.wizard"
    _description = "Partial Settlement Wizard"

    partner_id = fields.Many2one("res.partner")
    payment_id = fields.Many2one(
        "account.payment",
        string="Payment",
        domain=[
            ("partner_id", "=", partner_id),
            ("state", "=", "posted"),
            ("is_reconciled", "=", False),
        ],
    )

    total_invoice_due = fields.Monetary(compute="_compute_invoice_due")
    currency_id = fields.Many2one(
        "res.currency",
        related="partner_id.currency_id",
        readonly=True,
    )

    total_to_reconcile = fields.Monetary(
        compute="_compute_total_to_reconcile",
        store=True,
    )
    payment_residual = fields.Monetary(
        string="Payment Available",
        compute="_compute_payment_residual",
        store=True,
    )

    line_ids = fields.One2many(
        "partial.settlement.line",
        "wizard_id",
        string="Invoices",
    )

    payment_amount = fields.Monetary(compute="_compute_payment_amount")
    has_payments = fields.Boolean(compute="_compute_has_payments", store=False)

    @api.depends("partner_id")
    def _compute_has_payments(self):
        for rec in self:
            rec.has_payments = bool(
                self.env["account.payment"].search(
                    [
                        ("partner_id", "=", rec.partner_id.id),
                        ("state", "=", "posted"),
                        ("is_reconciled", "=", False),
                    ],
                    limit=1,
                )
            )

    @api.onchange("payment_id")
    def _onchange_payment_id(self):
        self.line_ids = [(5, 0, 0)]

        if not self.partner_id or not self.payment_id:
            return

        payment_type = self.payment_id.payment_type
        _logger.info(f"\n📌 Payment Type Selected: {payment_type}")

        if payment_type == "inbound":
            invoice_types = ["out_invoice", "out_refund"]
            _logger.info("🔎 Loading Customer Invoices and Credit Notes...")
        elif payment_type == "outbound":
            invoice_types = ["in_invoice", "in_refund"]
            _logger.info("🔎 Loading Vendor Bills and Refunds...")
        else:
            _logger.info("⚠️ Unknown payment type, skipping invoice loading.")
            return

        invoices = (
            self.env["account.move"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", self.partner_id.id),
                    ("move_type", "in", invoice_types),
                    ("payment_state", "in", ["not_paid", "partial"]),
                    ("state", "=", "posted"),
                ]
            )
        )

        _logger.info(f"🧾 Found {len(invoices)} eligible invoices for reconciliation.")

        self.line_ids = [
            (
                0,
                0,
                {
                    "invoice_id": inv.id,
                    "invoice_date": inv.invoice_date,
                    "amount_total": inv.amount_total,
                    "amount_due": inv.amount_residual,
                    "partial_amount": 0.0,
                },
            )
            for inv in invoices
        ]

    @api.onchange("line_ids")
    def _onchange_line_ids_payment_filter(self):
        if not self.partner_id:
            return

        in_types = ["in_invoice", "in_refund"]
        out_types = ["out_invoice", "out_refund"]

        in_count = sum(
            1 for line in self.line_ids if line.invoice_id.move_type in in_types
        )
        out_count = sum(
            1 for line in self.line_ids if line.invoice_id.move_type in out_types
        )

        is_vendor_context = in_count >= out_count

        _logger.info(
            f"🔍 Detected {'Vendor' if is_vendor_context else 'Customer'} context "
            "based on line_ids"
        )

        domain = [
            ("partner_id", "=", self.partner_id.id),
            ("state", "=", "posted"),
            ("is_reconciled", "=", False),
        ]

        if is_vendor_context:
            domain.append(("payment_type", "=", "outbound"))
        else:
            domain.append(("payment_type", "=", "inbound"))

        return {"domain": {"payment_id": domain}}

    @api.depends("payment_id")
    def _compute_payment_amount(self):
        for rec in self:
            rec.payment_amount = rec.payment_id.amount if rec.payment_id else 0.0

    @api.depends("partner_id")
    def _compute_invoice_due(self):
        for rec in self:
            moves = self.env["account.move"].search(
                [
                    ("partner_id", "=", rec.partner_id.id),
                    (
                        "move_type",
                        "in",
                        ["out_invoice", "in_invoice", "out_refund", "in_refund"],
                    ),
                    ("payment_state", "in", ["not_paid", "partial"]),
                    ("state", "=", "posted"),
                ]
            )
            rec.total_invoice_due = sum(m.amount_residual for m in moves)

    @api.depends("payment_id", "line_ids.partial_amount")
    def _compute_payment_residual(self):
        for rec in self:
            if rec.payment_id:
                residual = 0.0
                for line in rec.payment_id.move_id.line_ids:
                    if (
                        line.account_id.account_type
                        in ("asset_receivable", "liability_payable")
                        and not line.reconciled
                    ):
                        residual += (
                            line.amount_residual_currency or line.amount_residual
                        )
                rec.payment_residual = abs(residual)
            else:
                rec.payment_residual = 0.0

    @api.depends("line_ids.partial_amount")
    def _compute_total_to_reconcile(self):
        for rec in self:
            rec.total_to_reconcile = sum(rec.line_ids.mapped("partial_amount"))

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        self.payment_id = False
        self.line_ids = [(5, 0, 0)]
        if self.partner_id:
            return {
                "domain": {
                    "payment_id": [
                        ("partner_id", "=", self.partner_id.id),
                        ("state", "=", "posted"),
                        ("is_reconciled", "=", False),
                    ]
                }
            }

    def _is_receivable_or_payable(self, account):
        account_type = getattr(account, "account_type", None)
        if account_type:
            return account_type in ("asset_receivable", "liability_payable")
        legacy_type = getattr(account.user_type_id, "type", None)
        return legacy_type in ("receivable", "payable")
