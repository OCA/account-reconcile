# Copyright 2022 ForgeFlow S.L.
# @author Jordi Ballester <jordi.ballester@forgeflow.com.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def remove_move_reconcile(self):
        if self._context.get("skip_undo_reconciliation"):
            return True
        return super(AccountMoveLine, self).remove_move_reconcile()
