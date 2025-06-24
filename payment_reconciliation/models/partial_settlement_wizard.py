import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PartialSettlementLine(models.TransientModel):
    _name = "partial.settlement.line"
    _description = "Partial Settlement Line"

    wizard_id = fields.Many2one("partial.settlement.wizard", required=True)
    invoice_id = fields.Many2one("account.move")
    invoice_date = fields.Date()
    amount_total = fields.Monetary(string="Total Amount")
    amount_due = fields.Monetary(string="Pending Amount")
    partial_amount = fields.Monetary(string="Amount to Reconcile")
    currency_id = fields.Many2one(
        "res.currency", related="wizard_id.currency_id", readonly=True
    )


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

    def action_reconcile(self):
        self.ensure_one()

        if not self.payment_id:
            raise UserError(_("Please select a payment to reconcile."))

        if self.total_to_reconcile <= 0:
            raise UserError(_("Please enter amounts greater than 0 to reconcile."))

        payment_residual_abs = abs(self.payment_residual)

        if self.total_to_reconcile > payment_residual_abs + 0.01:
            raise UserError(
                _(
                    "The total partial amounts (%(total)s) exceed the available "
                    "payment amount (%(available)s)."
                )
                % {
                    "total": self.total_to_reconcile,
                    "available": payment_residual_abs,
                }
            )

        payment_lines = self.payment_id.move_id.line_ids.filtered(
            lambda line: line.account_id.account_type
            in ("asset_receivable", "liability_payable")
            and not line.reconciled
            and (line.amount_residual_currency or line.amount_residual)
            and abs(line.amount_residual_currency or line.amount_residual) > 0.0001
        )

        if not payment_lines:
            raise UserError(_("No reconcilable lines found in the payment."))

        _logger.info("✅ Available payment lines for reconciliation: %s", payment_lines)

        matched_invoice_ids = set()

        for line in self.line_ids:
            if not line.invoice_id:
                invoice = self.env["account.move"].search(
                    [
                        ("partner_id", "=", self.partner_id.id),
                        ("invoice_date", "=", line.invoice_date),
                        ("amount_total", "=", line.amount_total),
                        ("state", "=", "posted"),
                        (
                            "move_type",
                            "in",
                            ["out_invoice", "out_refund", "in_invoice", "in_refund"],
                        ),
                        ("amount_residual", "!=", 0),
                        ("id", "not in", list(matched_invoice_ids)),
                    ],
                    limit=1,
                )

                if invoice:
                    line.invoice_id = invoice
                    matched_invoice_ids.add(invoice.id)
                    _logger.info(
                        "🔗 Linked missing invoice: %s (Amount: %s) to line %s",
                        invoice.name,
                        invoice.amount_residual,
                        line.id,
                    )

        remaining_payment_amount = abs(
            sum(
                payment_lines.mapped(
                    lambda x: x.amount_residual_currency or x.amount_residual
                )
            )
        )

        for line in self.line_ids.filtered(
            lambda settlement_line: settlement_line.partial_amount > 0
        ):
            invoice = line.invoice_id

            if not invoice:
                continue

            if line.partial_amount > remaining_payment_amount + 0.01:
                raise UserError(
                    _(
                        "Partial amount %(partial)s exceeds remaining payment amount "
                        "%(remaining)s."
                    )
                    % {
                        "partial": line.partial_amount,
                        "remaining": remaining_payment_amount,
                    }
                )

            invoice_lines = invoice.line_ids.filtered(
                lambda line: line.account_id.account_type
                in ("asset_receivable", "liability_payable")
                and not line.reconciled
                and (line.amount_residual_currency or line.amount_residual)
                and abs(line.amount_residual_currency or line.amount_residual) > 0.0001
            )

            if not invoice_lines:
                continue

            payment_lines_to_reconcile = payment_lines.filtered(
                lambda payment_line,
                account_id=invoice_lines[0].account_id: payment_line.account_id
                == account_id
                and not payment_line.reconciled
                and (
                    payment_line.amount_residual_currency
                    or payment_line.amount_residual
                )
                and abs(
                    payment_line.amount_residual_currency
                    or payment_line.amount_residual
                )
                > 0.0001
            )

            if not payment_lines_to_reconcile:
                continue

            debit_line = invoice_lines[0]
            credit_line = payment_lines_to_reconcile[0]

            debit_residual = (
                debit_line.amount_residual_currency or debit_line.amount_residual
            )
            credit_residual = (
                credit_line.amount_residual_currency or credit_line.amount_residual
            )

            amount = min(
                abs(line.partial_amount),
                abs(debit_residual),
                abs(credit_residual),
                remaining_payment_amount,
            )

            if invoice.move_type in ["out_refund", "in_invoice"]:
                amount = -abs(amount)

            try:
                reconcile_vals = {
                    "debit_move_id": debit_line.id if amount >= 0 else credit_line.id,
                    "credit_move_id": credit_line.id if amount >= 0 else debit_line.id,
                    "amount": abs(amount),
                    "company_id": self.env.company.id,
                }

                if debit_line.amount_currency and credit_line.amount_currency:
                    reconcile_vals.update(
                        {
                            "debit_amount_currency": min(
                                abs(amount), abs(debit_line.amount_currency)
                            ),
                            "credit_amount_currency": min(
                                abs(amount), abs(credit_line.amount_currency)
                            ),
                            "debit_currency_id": debit_line.currency_id.id,
                            "credit_currency_id": credit_line.currency_id.id,
                        }
                    )

                self.env["account.partial.reconcile"].create(reconcile_vals)
                remaining_payment_amount -= abs(amount)

            except Exception as e:
                error_msg = _("❌ Failed to reconcile") % {
                    "amount": line.partial_amount,
                    "invoice": invoice.name,
                    "error": str(e),
                }
                raise UserError(error_msg) from e

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Reconciliation Complete"),
                "message": _("Partial settlement was successfully completed."),
                "sticky": False,
                "type": "success",
            },
        }
