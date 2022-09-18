# Copyright 2022 ForgeFlow S.L.
# @author Jordi Ballester <jordi.ballester@forgeflow.com.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def button_draft(self):
        moves_to_draft = self.filtered(lambda m: not m.statement_line_id.is_reconciled)
        return super(AccountMove, moves_to_draft).button_draft()
