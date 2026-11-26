# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from operator import itemgetter

from odoo import _, api, fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    # Allow changing payment mode in open state
    # TODO: Check if must be done in account_payment_partner instead
    payment_mode_id = fields.Many2one(
        states={"draft": [("readonly", False)], "posted": [("readonly", False)]}
    )
    payment_mode_warning = fields.Char(
        compute="_compute_payment_mode_warning",
    )
    display_payment_mode_warning = fields.Boolean(
        compute="_compute_payment_mode_warning",
    )

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for invoice in self:
            if invoice.move_type != "out_invoice":
                continue
            if not invoice.payment_mode_id.auto_reconcile_outstanding_credits:
                continue
            partial = invoice.payment_mode_id.auto_reconcile_allow_partial
            invoice.with_context(
                _payment_mode_auto_reconcile=True
            ).auto_reconcile_credits(partial_allowed=partial)
        return res

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        if "payment_mode_id" in vals or "state" in vals:
            for invoice in self:
                # Do not auto reconcile anything else than open customer inv
                if invoice.state != "posted" or invoice.move_type != "out_invoice":
                    continue
                invoice_lines = invoice.line_ids.filtered(
                    lambda line: line.account_type == "asset_receivable"
                )
                # Auto reconcile if payment mode sets it
                payment_mode = invoice.payment_mode_id
                if payment_mode and payment_mode.auto_reconcile_outstanding_credits:
                    partial = payment_mode.auto_reconcile_allow_partial
                    invoice.with_context(
                        _payment_mode_auto_reconcile=True
                    ).auto_reconcile_credits(partial_allowed=partial)
                # If the payment mode is not using auto reconcile we remove
                #  the existing reconciliations
                elif any(
                    [
                        invoice_lines.mapped("matched_credit_ids"),
                        invoice_lines.mapped("matched_debit_ids"),
                    ]
                ):
                    invoice.auto_unreconcile_credits()
        return res

    def auto_reconcile_credits(self, partial_allowed=True):
        for invoice in self:
            invoice._compute_payments_widget_to_reconcile_info()

            if not invoice.invoice_has_outstanding:
                continue
            credits_info = invoice.invoice_outstanding_credits_debits_widget
            # Get outstanding credits in chronological order
            # (using reverse because aml is sorted by date desc as default)
            credits_dict = credits_info.get("content", False)
            if invoice.payment_mode_id.auto_reconcile_same_journal:
                credits_dict = invoice._filter_payment_same_journal(credits_dict)
            sorted_credits = self._sort_credits_dict(credits_dict)
            for credit in sorted_credits:
                if (
                    not partial_allowed
                    and credit.get("amount") > invoice.amount_residual
                ):
                    continue
                invoice.js_assign_outstanding_line(credit.get("id"))

    @api.model
    def _sort_credits_dict(self, credits_dict):
        """Sort credits dict according to their id (oldest recs first)"""
        return sorted(credits_dict, key=itemgetter("id"))

    def _filter_payment_same_journal(self, credits_dict):
        """Keep only credits on the same journal than the invoice."""
        self.ensure_one()
        line_ids = [credit["id"] for credit in credits_dict]
        lines = self.env["account.move.line"].search(
            [("id", "in", line_ids), ("journal_id", "=", self.journal_id.id)]
        )
        return [credit for credit in credits_dict if credit["id"] in lines.ids]

    def auto_unreconcile_credits(self):
        for invoice in self:
            payments_info = invoice.invoice_payments_widget
            for payment in payments_info.get("content", []):
                payment_aml = (
                    self.env["account.payment"]
                    .browse(payment.get("account_payment_id"))
                    .line_ids
                )

                aml = payment_aml.filtered(lambda l: l.matched_debit_ids)
                for apr in aml.matched_debit_ids:
                    if apr.amount != payment.get("amount"):
                        continue
                    if (
                        apr.payment_mode_auto_reconcile
                        and apr.debit_move_id.move_id == invoice
                    ):
                        aml.remove_move_reconcile()

    @api.depends(
        "move_type", "payment_mode_id", "payment_id", "state", "invoice_has_outstanding"
    )
    def _compute_payment_mode_warning(self):
        # TODO Improve me but watch out
        for invoice in self:
            existed_reconciliations = any(
                [
                    invoice.line_ids.mapped("matched_credit_ids"),
                    invoice.line_ids.mapped("matched_debit_ids"),
                ]
            )
            if invoice.move_type != "out_invoice" or (
                invoice.state == "posted" and invoice.payment_state != "paid"
            ):
                invoice.payment_mode_warning = ""
                invoice.display_payment_mode_warning = False
                continue
            invoice.display_payment_mode_warning = True
            if (
                invoice.state != "posted"
                and invoice.payment_mode_id
                and invoice.payment_mode_id.auto_reconcile_outstanding_credits
            ):
                invoice.payment_mode_warning = _(
                    "Validating invoices with this payment mode will reconcile"
                    " any outstanding credits."
                )
            elif (
                invoice.state == "posted"
                and invoice.payment_state != "paid"
                and existed_reconciliations
                and (
                    not invoice.payment_mode_id
                    or not invoice.payment_mode_id.auto_reconcile_outstanding_credits
                )
            ):
                invoice.payment_mode_warning = _(
                    "Changing payment mode will unreconcile existing auto "
                    "reconciled payments."
                )
            elif (
                invoice.state == "posted"
                and invoice.payment_state != "paid"
                and not existed_reconciliations
                and invoice.payment_mode_id
                and invoice.payment_mode_id.auto_reconcile_outstanding_credits
                and invoice.invoice_has_outstanding
            ):
                invoice.payment_mode_warning = _(
                    "Changing payment mode will reconcile outstanding credits."
                )
            else:
                invoice.payment_mode_warning = ""
                invoice.display_payment_mode_warning = False
