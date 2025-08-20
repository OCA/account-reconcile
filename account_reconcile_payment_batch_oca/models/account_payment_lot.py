# Copyright 2024 Dixmit
# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPaymentLot(models.Model):
    _inherit = "account.payment.lot"

    is_matched = fields.Boolean(compute="_compute_matched_info", store=True)

    @api.depends("payment_ids.state")
    def _compute_matched_info(self):
        for lot in self:
            lot.is_matched = any([pay.state == "paid" for pay in lot.payment_ids])

    def open_form(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account_payment_batch_oca.account_payment_lot_action"
        )
        action.update(
            {
                "views": False,
                "view_mode": "form",
                "res_id": self.id,
            }
        )
        return action

    def _get_move_lines_to_reconcile(self, raise_if_none=True):
        self.ensure_one()
        valid_account_types = self.env[
            "account.payment"
        ]._get_valid_payment_account_types()
        move_lines = self.env["account.move.line"]
        for payment in self.payment_ids.filtered(lambda r: not r.is_matched):
            if payment.move_id:
                (
                    liquidity_lines,
                    _counterpart_lines,
                    _writeoff_lines,
                ) = payment._seek_for_lines()
                move_lines |= liquidity_lines
            else:
                for invoice in payment.invoice_ids:
                    move_lines |= invoice.line_ids.filtered(
                        lambda x: not x.reconciled
                        and x.account_id.account_type in valid_account_types
                        and x.display_type == "payment_term"
                    )

        if not move_lines and raise_if_none:
            raise UserError(
                _(
                    "The selected payment lot %s is made of payments that are already "
                    "reconciled or don't have a journal entry and are not "
                    "linked to invoices."
                )
                % self.name
            )
        return move_lines
