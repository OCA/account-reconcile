# Copyright 2026 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import _, models


class AccountBankStatementLine(models.Model):

    _inherit = "account.bank.statement.line"

    def _unreconcile_from_draft_moves(self, draft_moves, other_moves):
        """Put the statement line back to the reconciliation queue after some of
        the entries it was reconciled with have been reset to draft.
        """
        self.ensure_one()
        self.action_undo_reconciliation()
        # Drop the data kept by the reconciliation widget, so that it proposes
        # the counterparts again instead of the ones of the entries reset to draft.
        self.reconcile_data = False

        def _links(moves):
            return Markup(", ").join(
                Markup(
                    '<a href="#" data-oe-model="account.move" data-oe-id="%s">%s</a>'
                )
                % (move.id, move.name)
                for move in moves
            )

        body = Markup(
            _(
                "The statement line %(line)s is to reconcile again because "
                "%(moves)s has been reset to draft."
            )
        ) % {"line": self.payment_ref, "moves": _links(draft_moves)}
        if other_moves:
            body += Markup("<br/>") + Markup(
                _("Its reconciliation with %(moves)s has been undone as well.")
            ) % {"moves": _links(other_moves)}
        self.move_id.message_post(body=body)
