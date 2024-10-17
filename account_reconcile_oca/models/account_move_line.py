# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    paid_amount = fields.Monetary(
        compute="_compute_paid_amount",
        currency_field="company_currency_id",
    )

    def _compute_paid_amount(self):
        account_bank_statement_line_obj = self.env["account.bank.statement.line"]
        for rec in self:
            paid_amount = 0.0
            st_line = account_bank_statement_line_obj.browse(
                self._context.get("bank_statement_line_id")
            )
            if st_line.is_reconciled:
                (
                    _liquidity_lines,
                    suspense_lines,
                    _other_lines,
                ) = st_line._seek_for_lines()
                if _other_lines:
                    paid_amount += sum(
                        _other_lines.mapped("matched_debit_ids")
                        .filtered(lambda mdi: mdi.debit_move_id == rec)
                        .mapped("amount")
                    )
                    paid_amount += sum(
                        _other_lines.mapped("matched_credit_ids")
                        .filtered(lambda mdi: mdi.credit_move_id == rec)
                        .mapped("amount")
                    )
            rec.paid_amount = paid_amount

    def action_reconcile_manually(self):
        if not self:
            return {}
        accounts = self.mapped("account_id")
        if len(accounts) > 1:
            raise ValidationError(
                _("You can only reconcile journal items belonging to the same account.")
            )
        partner = self.mapped("partner_id")
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_reconcile_oca.account_account_reconcile_act_window"
        )
        action["domain"] = [("account_id", "=", self.mapped("account_id").id)]
        if len(partner) == 1 and self.account_id.account_type in [
            "asset_receivable",
            "liability_payable",
        ]:
            action["domain"] += [("partner_id", "=", partner.id)]
        action["context"] = self.env.context.copy()
        action["context"]["default_account_move_lines"] = self.filtered(
            lambda r: not r.reconciled
        ).ids
        return action
