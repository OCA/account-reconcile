# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import ValidationError
from odoo.tools.sql import create_index


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def init(self):
        """Index the candidate counterparts of the reconcile widget.

        The `add_account_move_line_id` field of the reconcile view searches the
        counterparts with the domain::

            [("parent_state", "=", "posted"), ("amount_residual", "!=", 0),
             ("account_id.reconcile", "=", True), ("company_id", "=", company_id),
             ("statement_line_id", "!=", id)]

        No index of the ``account`` module supports it: the standard
        ``account_move_line__unreconciled_index`` is built on ``reconciled``,
        not on ``amount_residual``. On big databases that means a full scan of
        ``account_move_line`` on every single interaction with the widget,
        because ``web_search_read`` also runs a ``search_count`` for the pager.
        """
        res = super().init()
        create_index(
            self.env.cr,
            "account_move_line_reconcile_widget_idx",
            self._table,
            ["company_id", "account_id", "partner_id", "statement_line_id"],
            where="parent_state = 'posted' AND amount_residual <> 0",
        )
        create_index(
            self.env.cr,
            "account_move_line_reconcile_order_idx",
            self._table,
            ["date DESC", "move_name DESC", "id"],
            where="parent_state = 'posted' AND amount_residual <> 0",
        )
        return res

    def action_reconcile_manually(self):
        if not self:
            return {}
        accounts = self.mapped("account_id")
        if len(accounts) > 1:
            raise ValidationError(
                self.env._(
                    "You can only reconcile journal items belonging to the"
                    " same account."
                )
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
