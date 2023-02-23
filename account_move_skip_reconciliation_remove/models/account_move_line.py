from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def remove_move_reconcile(self):
        if not self._context.get("skip_remove_reconciliation", False):
            return super().remove_move_reconcile()
