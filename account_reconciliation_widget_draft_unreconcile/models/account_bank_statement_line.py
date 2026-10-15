# Copyright 2026 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from markupsafe import escape

from odoo import _, models


class AccountBankStatementLine(models.Model):

    _inherit = "account.bank.statement.line"

    def _unreconcile_from_draft_moves(self, draft_moves, other_moves):
        """Put the statement line back to the reconciliation queue after some of
        the entries it was reconciled with have been reset to draft.
        """
        self.ensure_one()
        statement = self.statement_id
        # A validated statement only holds reconciled lines.
        if statement.state == "confirm":
            statement.button_reprocess()
        self.button_undo_reconciliation()

        def _links(moves):
            return ", ".join(
                '<a href="#" data-oe-model="account.move" data-oe-id="%s">%s</a>'
                % (move.id, escape(move.name))
                for move in moves
            )

        body = _(
            "The statement line %(line)s is to reconcile again because "
            "%(moves)s has been reset to draft.",
            line=escape(self.payment_ref),
            moves=_links(draft_moves),
        )
        if other_moves:
            body += "<br/>" + _(
                "Its reconciliation with %(moves)s has been undone as well.",
                moves=_links(other_moves),
            )
        statement.message_post(body=body)
