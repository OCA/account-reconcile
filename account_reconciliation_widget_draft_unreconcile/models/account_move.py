# Copyright 2026 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):

    _inherit = "account.move"

    def _get_reconciled_statement_lines(self):
        """Return a dict {statement line: moves} with the bank statement lines
        reconciled through the widget against the journal items of self, and
        all the moves each statement line is reconciled with.
        """
        lines = self.line_ids
        partials = lines.matched_debit_ids | lines.matched_credit_ids
        counterparts = (partials.debit_move_id | partials.credit_move_id) - lines
        st_lines = counterparts.move_id.statement_line_id.filtered(
            # Statement lines whose own entry is being reset to draft (statement
            # reopen, reconciliation process...) are already handled by the caller.
            # Statement lines matched against an existing payment (blue lines)
            # keep that payment, which is still a valid counterpart.
            lambda st_line: st_line.move_id not in self
            and not st_line.move_id.payment_id
        )
        res = {}
        for st_line in st_lines:
            st_move_lines = st_line.move_id.line_ids
            st_partials = st_move_lines.matched_debit_ids | (
                st_move_lines.matched_credit_ids
            )
            res[st_line] = (
                st_partials.debit_move_id | st_partials.credit_move_id
            ).move_id - st_line.move_id
        return res

    def button_draft(self):
        st_lines_moves = self._get_reconciled_statement_lines()
        res = super().button_draft()
        for st_line, moves in st_lines_moves.items():
            # Users allowed to reset an entry to draft (billing) may not be
            # allowed to modify bank statement lines.
            st_line.sudo()._unreconcile_from_draft_moves(moves & self, moves - self)
        return res
